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
from .models import File, Message, Analysis, Person, Location, KeywordSuite, RiskWord

# default_suite = Keywords()


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
        risk_words = RiskWord.objects.all()

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
    
    
    
def settings_page(request):
    keyword_suites = KeywordSuite.objects.all()
    suite = keyword_suites[0]
    risk_words = RiskWord.objects.filter(suite=suite)

    context_dict = {'keyword_suites': keyword_suites, 'risk_words':risk_words}

    return render(request, "conversation_analyst/settings.html", context=context_dict)


def create_suite(request):
    if request.method == 'POST':
        suite_name = request.POST['name']
        suite_obj = KeywordSuite.objects.create(name=suite_name)
        suite_obj.save()
        context_dict = {'message': 'New suite added', 'suiteId': suite_obj.id}
        return JsonResponse(context_dict)
    
def delete_suite(request):
    if request.method == 'GET':
        suite_id = request.GET['suiteId']
        suite_obj = KeywordSuite.objects.get(id=suite_id)
        RiskWord.objects.filter(suite=suite_obj).delete()
        suite_obj.delete()
        return HttpResponse('suite deleted')
        
        
def select_suite(request):
    if request.method == 'GET':
        suite_name = request.GET['suite'].strip()
        suite = KeywordSuite.objects.get(name=suite_name)
        keywords = RiskWord.objects.filter(suite=suite)
        # field_values_1 = [obj.your_field for obj in your_objects_queryset]
        serialized_keywords = serialize('json', keywords)
        return JsonResponse({'objects': serialized_keywords}, safe=False)
    
def create_keyword(request):
    if request.method == 'POST':
        keyword = request.POST['keyword']
        suite_name = request.POST['suite'].strip()
        suite = KeywordSuite.objects.get(name=suite_name)
        keyword_obj = RiskWord.objects.create(suite=suite,keyword=keyword)
        keyword_obj.save()
        context_dict = {'message': 'New keyword added', 'keywordId': keyword_obj.id}
        return JsonResponse(context_dict)
    
    
def delete_keyword(request):
    if request.method == 'GET':
        keyword_id = request.GET['keywordId']
        RiskWord.objects.get(id=keyword_id).delete()
        return HttpResponse('keyword deleted')

# def demo_keywords():
#     if default_suite.has_keywords() == False:
#         default_suite.add_keyword("perfect", ["Good", "Really Good"], 8)
#         default_suite.add_keyword("old", ["Time"], 2)
#         default_suite.add_keyword("nice", ["Good"], 3)
#         default_suite.add_keyword("galaxy", ["Space", "Time"], 5)
#         default_suite.add_keyword("amazing", ["Awesome", "Fantastic"], 7)
#         default_suite.add_keyword("young", ["Youthful"], 4)
#         default_suite.add_keyword("awesome", ["Great", "Fantastic"], 6)
#         default_suite.add_keyword("technology", ["Innovation", "Science"], 9)
#         default_suite.add_keyword("beautiful", ["Attractive", "Stunning"], 5)
#         default_suite.add_keyword("community", ["Society", "Neighbors"], 5)
#         default_suite.add_keyword("innovation", ["Creativity", "Invention"], 6)
#         default_suite.add_keyword("cozy", ["Comfortable", "Warm"], 4)
#         default_suite.add_keyword("delicious", ["Tasty", "Yummy"], 7)
#         default_suite.add_keyword("friendship", ["Companionship", "Buddy"], 6)
#         default_suite.add_keyword("relaxing", ["Calming", "Unwinding"], 5)
#         default_suite.add_keyword("celebration", ["Party", "Festivity"], 8)
#         default_suite.add_keyword("curious", ["Inquisitive", "Interested"], 5)
#         default_suite.add_keyword("efficient", ["Productive", "Streamlined"], 7)
#         default_suite.add_keyword("refreshing", ["Invigorating", "Revitalizing"], 6)
#     return default_suite
