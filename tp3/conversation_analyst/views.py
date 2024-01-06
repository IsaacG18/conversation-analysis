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




import os
from django.conf import settings

from .forms import UploadFileForm
from .models import File, Message, Analysis, Person, Location, RiskWord


# Create your views here.
def homepage(request):
    files = File.objects.order_by('-date') # newest at the top
    return render(request, "conversation_analyst/homepage.html", {"files": files})

def validate_delimiters(delimiters):
    for delimiter in delimiters:
        if not delimiter[1].strip():
            return False
    return True

def upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # get file delimeters
            sender = form.cleaned_data.get('sender_delim')
            timestamp = form.cleaned_data.get('timestamp_delim')
            custom = form.cleaned_data.get('custom_delim')
            file_delimeters = [["Timestamp", timestamp], ["Sender", sender]]
            
            # Create file object
            uploaded_file = request.FILES["file"]

            # Check if delimiters are valid for the given file
            if not validate_delimiters_for_file(uploaded_file, file_delimeters):
                # Handle invalid delimiters (e.g., return an error message)
                return HttpResponse("Invalid delimiters provided", status=400)

            # Save the file and process
            file_obj = File.objects.create(file=uploaded_file)
            file_obj.save()
            process_file(file_obj, delimiters=file_delimeters)

            # Display file analysis
            return HttpResponseRedirect(reverse('content_review', kwargs={'file_slug': file_obj.slug}))

    else:
        form = UploadFileForm()
    return render(request, "conversation_analyst/upload.html", {"form": form})

def validate_delimiters_for_file(uploaded_file, delimiters):
    try:
        for _ in range(5):
            line = uploaded_file.readline().decode()
            if not line:
                break
            if not validate_delimiters_in_line(line, delimiters):
                return False
        return True
    except Exception as e:
        print(f"Error during validation: {e}")
        return False
    
def validate_delimiters_in_line(line, delimiters):
    parts = line.split(delimiters[0][1])
    if len(parts) < 2:
        return False

    subparts = parts[1].split(delimiters[1][1])
    if len(subparts) < 2:
        return False

    # Additional checks can be added here based on the expected structure
    return True


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
        
