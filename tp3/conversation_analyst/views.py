from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

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
