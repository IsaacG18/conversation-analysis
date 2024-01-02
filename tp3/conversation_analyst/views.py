from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .scripts.data_ingestion import ingestion
from .scripts.nlp.nlp import *
from .scripts.object_creators import *
from django.core.serializers import serialize
from itertools import chain
from django.utils import timezone
from datetime import datetime
import json
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom




import os
from django.conf import settings

from .forms import UploadFileForm
from .models import File, Message, Analysis, Person, Location, RiskWord


# Create your views here.
def homepage(request):
    files = File.objects.order_by('-date') # newest at the top
    return render(request, "conversation_analyst/homepage.html", {"files": files})


def upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # create file object
            uploaded = request.FILES["file"]
            file_obj = File.objects.create(file=uploaded)
            file_obj.save()
            process_file(file_obj)
            # display file analysis
            return HttpResponseRedirect(reverse('content_review', kwargs={'file_slug': file_obj.slug}))
    else:
        form = UploadFileForm()
    return render(request, "conversation_analyst/upload.html", {"form": form})


def content_review(request, file_slug):
    try:
        file = File.objects.get(slug=file_slug)
        messages = Message.objects.filter(file=file)
        analysis = Analysis.objects.get(file=file)
        persons = Person.objects.filter(analysis=analysis)
        locations = Location.objects.filter(analysis=analysis)
        risk_words = RiskWord.objects.filter(analysis=analysis)

        context_dict = {'messages': messages, 'persons': persons,
                        'locations': locations, 'risk_words': risk_words, 'file': file}

        return render(request, "conversation_analyst/content_review.html", context=context_dict)

    except File.DoesNotExist:
        return HttpResponse("File not exist")



def process_file(file, delimiters=[["Timestamp", ","], ["Sender", ":"]], keywords=Keywords()):
    directory = os.path.join(settings.MEDIA_ROOT, 'uploads')
    file_path = os.path.join(directory, file.title)

    chat_messages = ingestion.parse_chat_file(file_path, delimiters)
    message_count = create_arrays(chat_messages)
    nlp_text, person_and_locations = tag_text(chat_messages, keywords, ["PERSON", "GPE"])
    risk_words = get_top_n_risk_keywords(nlp_text, 3)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)
    generate_analysis_objects(file,chat_messages, message_count,person_and_locations,risk_words,common_topics)


def generate_analysis_objects(file, chat_messages, message_count, person_and_locations, risk_words, common_topics):
    persons = person_and_locations['PERSON']
    locations = person_and_locations['GPE']

    for message in chat_messages:
        m = add_message(file, message['Timestamp'], message['Sender'], message['Message'], message["Display_Message"])
    a = add_analysis(file)
    for person in persons:
        p = add_person(a, person)
    for location in locations:
        p = add_location(a, location)
    for risk_word in risk_words:
        r = add_risk_word(a, risk_word[0], risk_word[1], risk_word[2])


def filter_view(request):
    filter_buttons = request.GET.get('filters','[]')
    filter_buttons = json.loads(filter_buttons)
    file_slug = request.GET['file_slug']
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    print(filter_buttons)
    filter_buttons

    try:
        file = File.objects.get(slug=file_slug)
        filter_params = {'file': file}
        if start_date: 
            filter_params['timestamp__gte'] = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        if end_date:
            filter_params['timestamp__lte'] = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')

        
        messages = Message.objects.filter(**filter_params)
        analysis = Analysis.objects.get(file=file)
        persons = Person.objects.filter(analysis=analysis)
        locations = Location.objects.filter(analysis=analysis)
        risk_words = RiskWord.objects.filter(analysis=analysis)
        print(filter_buttons)
        if len(filter_buttons)> 0:
            return_messages = []
            if filter_buttons[0]:
                return_messages = messages.filter(content__icontains=filter_buttons[0])
            if len(filter_buttons)> 1:
                for filter_button in filter_buttons[1]:
                    if filter_button:
                        return_messages = chain(return_messages, messages.filter(content__icontains=filter_button))
            messages = set(list(return_messages))

    except Exception as e:
        print(e)
        return JsonResponse({'result': 'error', 'message': 'Internal Server Error'})

    context_dict = {'messages': serialize('json', messages), 'persons': serialize('json', persons),
                        'locations': serialize('json', locations), 'risk_words': serialize('json', risk_words)}
    return JsonResponse(context_dict)
        
def export_view(request, file_slug):
    file = File.objects.get(slug=file_slug)
    messages = Message.objects.filter(file=file)
    analysis = Analysis.objects.get(file=file)
    persons = Person.objects.filter(analysis=analysis)
    locations = Location.objects.filter(analysis=analysis)
    risk_words = RiskWord.objects.filter(analysis=analysis)

    root = Element('exported_data')

    persons_element = SubElement(root, 'persons')
    for person in persons:
        entry_element = SubElement(persons_element, 'person')
        SubElement(entry_element, 'name').text = person.name

    locations_element = SubElement(root, 'locations')
    for location in locations:
        entry_element = SubElement(locations_element, 'location')
        SubElement(entry_element, 'name').text = location.name

    risk_words_element = SubElement(root, 'risk_words')
    for risk_word in risk_words:
        entry_element = SubElement(risk_words_element, 'risk_word')
        SubElement(entry_element, 'keyword').text = risk_word.keyword
        SubElement(entry_element, 'risk_factor').text = str(risk_word.risk_factor)
        SubElement(entry_element, 'amount').text = str(risk_word.amount)

    messages_element = SubElement(root, 'messages')
    for message in messages:
        entry_element = SubElement(messages_element, 'message')
        SubElement(entry_element, 'timestamp').text = str(message.timestamp)
        SubElement(entry_element, 'sender').text = message.sender
        SubElement(entry_element, 'content').text = message.content
        SubElement(entry_element, 'display_content').text = message.display_content
    xml_data = minidom.parseString(tostring(root)).toprettyxml(indent="  ")

    response = HttpResponse(xml_data, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="{file_slug}_exported_data.xml"'
    return response
        