from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .scripts.data_ingestion import ingestion
from .scripts.nlp.nlp import *
from .scripts.object_creators import *

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
                        'locations': locations, 'risk_words': risk_words}

        return render(request, "conversation_analyst/content_review.html", context=context_dict)

    except File.DoesNotExist:
        return HttpResponse("File not exist")

def json_content_review(request, file_slug):
    try:
        file = File.objects.get(slug=file_slug)
        messages = Message.objects.filter(file=file)
        analysis = Analysis.objects.get(file=file)
        persons = Person.objects.filter(analysis=analysis)
        locations = Location.objects.filter(analysis=analysis)
        risk_words = RiskWord.objects.filter(analysis=analysis)

        # Assuming buttonValue is sent as a POST parameter
        button_value = request.POST.get('value', None)

        # Filter messages based on button value
        if button_value:
            messages = messages.filter(content__icontains=button_value)

        messages_list = [{'content': message.content, 'created_at': message.created_at} for message in messages]

        response_data = {
            'messages': messages_list,
            'persons': [person.name for person in persons],
            'locations': [location.name for location in locations],
            'risk_words': [risk_word.word for risk_word in risk_words]
        }

        return JsonResponse(response_data)

    except File.DoesNotExist:
        return JsonResponse({'error': 'File not found'})



def process_file(file, delimiters=[["Timestamp", ","], ["Sender", ":"]], keywords=Keywords()):
    directory = os.path.join(settings.MEDIA_ROOT, 'uploads')
    file_path = os.path.join(directory, file.title)

    chat_messages = ingestion.parse_chat_file(file_path, delimiters)
    message_count = create_arrays(chat_messages)
    nlp_text = tag_text(chat_messages, keywords)
    person_and_locations = extract(nlp_text, ["PERSON", "GPE"])
    risk_words = get_top_n_risk_keywords(nlp_text, 3)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)

    generate_analysis_objects(file,chat_messages, message_count,person_and_locations,risk_words,common_topics)


def generate_analysis_objects(file, chat_messages, message_count, person_and_locations, risk_words, common_topics):
    persons = person_and_locations['PERSON']
    locations = person_and_locations['GPE']

    for message in chat_messages:
        m = add_message(file, message['Timestamp'], message['Sender'], message['Message'])
    a = add_analysis(file)
    for person in persons:
        p = add_person(a, person)
    for location in locations:
        p = add_location(a, location)
    for risk_word in risk_words:
        r = add_risk_word(a, risk_word[0], risk_word[1], risk_word[2])
