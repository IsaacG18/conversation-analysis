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
from openai import OpenAI


import os
from django.conf import settings

from .forms import UploadFileForm
from .models import File, Message, Analysis, Person, Location, KeywordSuite, RiskWord, KeywordPlan, Topic, RiskWordResult, VisFile, DateFormat, ChatGPTConvo

# default_suite = Keywords()


def homepage(request, query=None):
    files = File.objects.order_by('-date')
    try:
        query = request.GET['query']
        if len(query) > 0 and query.strip() != "":
            files=files.filter(title__icontains=query)
        return render(request, "conversation_analyst/search_result.html", {"files": files})
    except KeyError:
        return render(request, "conversation_analyst/homepage.html", {"files": files})

def upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():       
            # get file delimeters
            sender = form.cleaned_data.get('sender_delim')
            timestamp = form.cleaned_data.get('timestamp_delim')
            file_delimeters = [["Timestamp", timestamp], ["Sender", sender]]

            # Create file object
            uploaded_file = request.FILES["file"]

            # Save the file and process
            file_obj = File.objects.create(file=uploaded_file)
            file_obj.init_save()
            default_plan = KeywordPlan.objects.get_or_create(name='global')[0]
            keyword_suites = default_plan.keywordsuite_set.all()
            keywords = RiskWord.objects.filter(suite__in=keyword_suites)
            try:
                process_file(file_obj, delimiters=file_delimeters, keywords=keywords)
                return HttpResponseRedirect(reverse('content_review', kwargs={'file_slug': file_obj.slug}))
            except ValueError as e:
                file_obj.delete()
                return render(request, "conversation_analyst/upload.html", {"form": form, "error_message": str(e)})
            except ValidationError as e:
                file_obj.delete()
                return render(request, "conversation_analyst/upload.html", {"form": form, "error_message": str(e)})
    else:
        form = UploadFileForm()
    return render(request, "conversation_analyst/upload.html", {"form": form})

def content_review(request, file_slug):
    try:
        file = File.objects.get(slug=file_slug)
        messages = Message.objects.filter(file=file)
        for message in messages:
            message.set_main_sender(messages[0].sender)
        analysis = Analysis.objects.get(file=file)
        persons = Person.objects.filter(analysis=analysis)
        locations = Location.objects.filter(analysis=analysis)
        risk_words = RiskWordResult.objects.filter(analysis=analysis)
        vis_path = VisFile.objects.filter(analysis=analysis)

        context_dict = {'messages': messages, 'persons': persons,
                        'locations': locations, 'risk_words': risk_words, 'vis_path': vis_path[0].file_path, "file":file}

        return render(request, "conversation_analyst/content_review.html", context=context_dict)

    except File.DoesNotExist:
        return HttpResponse("File not exist")



def process_file(file, delimiters=[["Timestamp", ","], ["Sender", ":"]], keywords=Keywords()):
    directory = os.path.join(settings.MEDIA_ROOT, 'uploads')
    file_path = os.path.join(directory, file.title)

    if not file.title.endswith(('.docx', '.txt', '.csv')):
        raise ValueError("Unsupported file type. Only .txt, .csv and .docx are supported.")


    chat_messages = ingestion.parse_chat_file(file_path, delimiters)
    message_count = create_arrays(chat_messages)
    nlp_text, person_and_locations = tag_text(chat_messages, keywords, ["PERSON", "GPE"])
    risk_words = get_top_n_risk_keywords(nlp_text, 10)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)
    generate_analysis_objects(file,chat_messages, message_count,person_and_locations,risk_words,common_topics)


def generate_analysis_objects(file, chat_messages, message_count, person_and_locations, risk_words, common_topics):
    persons = person_and_locations['PERSON']
    locations = person_and_locations['GPE']

    for message in chat_messages:
        m = add_message(file, message['Timestamp'], message['Sender'], message['Message'], message["Display_Message"],  message["risk"])
    a = add_analysis(file)
    add_vis(a, plots(chat_messages, file.slug))
    for person in persons:
        p = add_person(a, person)
    for location in locations:
        p = add_location(a, location)
    for risk_word in risk_words:
        r = add_risk_word_result(a, risk_word[0], risk_word[2], risk_word[1])


def filter_view(request):
    filters = request.GET.get('filters','[]')
    filters = json.loads(filters)
    file_slug = request.GET['file_slug']
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    risk = request.GET.get('risk','[]')
    risk = json.loads(risk)
    
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
        risk_words = RiskWordResult.objects.filter(analysis=analysis)
        if len(filters)> 0:
            filter_condition = Q()
            for word in filters:
                search_term = r'(?<![a-zA-Z0-9]){}(?![a-zA-Z0-9])'.format(word)
                filter_condition |= Q(content__iregex=search_term)
            messages = messages.filter(filter_condition)
        
        if len(risk)> 0:
            filter_condition = Q()
            for risk_number in risk:
                filter_condition |= Q(risk_rating=risk_number)
            messages = messages.filter(filter_condition)
    except Exception as e:
        print(e)
        return JsonResponse({'result': 'error', 'message': 'Internal Server Error'})
    return JsonResponse({"results": render_to_string('conversation_analyst/messages.html', {'messages': messages, 'persons': persons,
                        'locations': locations, 'risk_words': risk_words})})


    
    
    
def settings_page(request):
    keyword_suites = KeywordSuite.objects.all()
    if len(keyword_suites) == 0:
        context_dict = {}
    else:
        suite = keyword_suites[0]
        risk_words = RiskWord.objects.filter(suite=suite)
        context_dict = {'keyword_suites': keyword_suites, 'risk_words':risk_words}

    return render(request, "conversation_analyst/settings.html", context=context_dict)


def create_suite(request):
    if request.method == 'POST':
        try:
            suite_name = request.POST['name']
            suite_obj = KeywordSuite.objects.create(name=suite_name)
            suite_obj.save()
            context_dict = {'message': 'New suite added', 'suiteId': suite_obj.id}
            return JsonResponse(context_dict, status=201)
        except IntegrityError as e:
            # print(e)
            return JsonResponse({'message': 'Suite name has to be unique'},status=500)  
    
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
        risk = request.POST['risk']
        suite = KeywordSuite.objects.get(name=suite_name)
        keyword_obj = RiskWord.objects.create(suite=suite,keyword=keyword,risk_factor=risk)
        keyword_obj.save()
        
        context_dict = {'message': 'New keyword added', 'keywordId': keyword_obj.id}
        return JsonResponse(context_dict)
    
    
def delete_keyword(request):
    if request.method == 'GET':
        keyword_id = request.GET['keywordId']
        RiskWord.objects.get(id=keyword_id).delete()
        return HttpResponse('keyword deleted')

  
def check_suite(request):
    if request.method == 'POST':
        response = ''
        suite_id = request.POST['suiteId']
        isChecked = json.loads(request.POST['value'])
        suite = KeywordSuite.objects.get(id=suite_id)
        keyword_plan = KeywordPlan.objects.get_or_create(name='global')[0]
        is_keyword_in_plan = keyword_plan in suite.plans.all()
        if (is_keyword_in_plan != isChecked):
            print(isChecked)
            if (isChecked):
                suite.plans.add(keyword_plan)
                suite.default = True
                response+="checked"
            else:
                suite.plans.remove(keyword_plan)
                suite.default = False
                response+="unchecked"
        suite.save()
        print(suite.plans.all())
        return HttpResponse(suite.name + " is " + response + " in " + keyword_plan.name + " plan")
    
    
def risk_update(request):
    if request.method == 'POST':
        keywordId = request.POST['keyword']
        risk = int(request.POST['risk'])
        keyword_obj = RiskWord.objects.filter(id=keywordId).first()
        keyword_obj.risk_factor = risk
        keyword_obj.save()
        
        return HttpResponse("risk factor of " + keyword_obj.keyword + " is updated to " + str(risk))
    
    
def rename_file(request):
    if request.method == 'POST':
        try: 
            newTitle = request.POST['fileName']
            fileId = request.POST['fileId']
            file_obj = File.objects.filter(id=fileId).first()
            fullTitle = newTitle+"."+file_obj.format
            file_obj.title = fullTitle
            file_obj.save()
            
            context_dict = {'message': "file name of file " + str(file_obj.id) + " is updated to " + fullTitle,
                            'fileName': fullTitle}
            return JsonResponse(context_dict)
        
        except Exception as e:
            print(e)
        return JsonResponse({'message': 'error'})

        
def export_view(request, file_slug):
    file = File.objects.get(slug=file_slug)
    messages = Message.objects.filter(file=file)
    analysis = Analysis.objects.get(file=file)
    persons = Person.objects.filter(analysis=analysis)
    locations = Location.objects.filter(analysis=analysis)
    risk_words = RiskWordResult.objects.filter(analysis=analysis)

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
        SubElement(entry_element, 'keyword').text = risk_word.riskword.keyword
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


        

def chatgpt_new_message(request):
    file_slug = request.GET['file_slug']
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    try:
        file = File.objects.get(slug=file_slug)
        filter_params = {'file': file}
        if start_date: 
            filter_params['timestamp__gte'] = datetime.strptime(start_date, '%Y-%m-%dT%H:%M')
        if end_date:
            filter_params['timestamp__lte'] = datetime.strptime(end_date, '%Y-%m-%dT%H:%M')
        messages = Message.objects.filter(**filter_params)
        convo = ChatGPTConvo.objects.create(file=uploaded_file, start = start_date, end = end_date)
        convo.init_save()

        system_message = "You are answering questions about a some text messages with lots of detail, the formated of the messages will be'<Timestamp>: <Name>: <Message> \n"
        for message in messages:
            system_message += f"{message.timestamp}: {message.sender}:  {message.content} \n"

        add_chat_message("system", system_message, convo)

    except Exception as e:
        print(e)
        return JsonResponse({'result': 'error', 'message': 'Internal Server Error'})


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
