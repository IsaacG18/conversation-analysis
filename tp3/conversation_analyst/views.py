from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .scripts.data_ingestion import ingestion
from .scripts.nlp.Keywords import *
from .scripts.nlp.nlp import *


import os
from django.conf import settings

from .forms import UploadFileForm
from .models import File, Message, Analysis, Person, Location, RiskWord


# Create your views here.
def homepage(request):
    files = File.objects.order_by('-date')
    return render(request, "conversation_analyst/homepage.html", {"files": files})

def upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = request.FILES["file"]
            title = str(uploaded)
            file_obj = File.objects.create(file=uploaded)
            file_obj.save()
            # Specify the directory where you want to save or process the file
            directory = os.path.join(settings.MEDIA_ROOT, 'uploads')
            file_path = os.path.join(directory, file_obj.file.name)
            process_file(file_path)
            return HttpResponseRedirect(reverse('content_review'))
    else:
        form = UploadFileForm()
    return render(request, "conversation_analyst/upload.html", {"form": form})
def content_review(request):
    messages = Message.objects.all()
    analysis = Analysis.objects.get(pk=1)
    persons = Person.objects.filter(analysis=analysis)
    locations = Location.objects.filter(analysis=analysis)
    risk_words = RiskWord.objects.filter(analysis=analysis)

    context_dict = {'messages': messages, 'persons': persons,
                    'locations': locations, 'risk_words': risk_words}

    return render(request, "conversation_analyst/content_review.html", context=context_dict)

def process_file(file_path, delimiters =[["Timestamp", ","], ["Sender", ":"]], keywords = Keywords()):
    chat_messages = ingestion.parse_chat_file(file_path, delimiters)
    message_count = create_arrays(chat_messages)
    nlp_text = tag_text(message_to_text(chat_messages), keywords)
    person_and_locations = extract(nlp_text, ["PERSON", "GPE"])
    risk_words = get_top_n_risk_keywords(nlp_text, 3)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)
    return chat_messages, message_count,person_and_locations,risk_words,common_topics
