from django.forms import ValidationError
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .scripts.data_ingestion.file_process import parse_file, process_file
from .scripts.object_creators import add_chat_message, add_chat_filter
from django.core.serializers import serialize
from django.db import IntegrityError
from datetime import datetime
from django.template.loader import render_to_string
from django.db.models import Q
import json
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from openai import OpenAI
import openai
import os

from .forms import UploadFileForm
from .models import (
    File,
    Message,
    Analysis,
    Person,
    Location,
    KeywordSuite,
    RiskWord,
    RiskWordResult,
    VisFile,
    DateFormat,
    Delimiter,
    ChatGPTConvo,
    ChatGPTMessage,
    CustomThresholds,
    GptSwitch,
    LastFile
)


def homepage(request, query=None):
    # Define the homepage view function.
    # clean up file without matching analysis
    # Displays a list of files ordered by date.
    # Handles search queries if provided, filtering files by title.

    # cleaning up un-analysed file
    if tracker := LastFile.objects.filter(id=1).first():
        if file := tracker.file:
            analysis = Analysis.objects.filter(file=tracker.file).first()
            if not analysis:
                print(f"deleting file {file.title}")
                file.delete()
    # show files
    files = File.objects.order_by("-date")
    try:
        query = request.GET["query"]
        if len(query) > 0 and query.strip() != "":
            files = files.filter(title__icontains=query)
        return render(
            request, "conversation_analyst/search_result.html", {"files": files}
        )
    except KeyError:
        return render(request, "conversation_analyst/homepage.html", {"files": files})


def upload(request):
    # Define the upload view function.
    # Handles file upload via form submission.
    # Parses the uploaded file, saves it, and redirects to suite selection.
    # Handles errors during file processing and displays appropriate messages.
    try:
        if request.method == "POST":
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                delims = Delimiter.objects.filter(order__gt=0).order_by("order")
                delim_pairs = [[delim.name, delim.value] for delim in delims]
                uploaded_file = request.FILES["file"]
                file_obj = File.objects.create(file=uploaded_file)
                file_obj.init_save()
                tracker = LastFile.objects.get_or_create(id=1)[0]
                tracker.file = file_obj
                tracker.save()
                timestamp = DateFormat.objects.get(
                    name=request.POST["selected_timestamp"]
                )
                skip = request.POST.get('selected_skip', False)
                if skip:
                    skip = True
                parse_file(file_obj, timestamp.format, skip=skip, delimiters=delim_pairs)
                return HttpResponseRedirect(
                    reverse("suite_selection", kwargs={"file_slug": file_obj.slug})
                )
    except (ValueError, ValidationError) as e:
        file_obj.delete()
        return render(
            request,
            "conversation_analyst/upload.html",
            {
                "form": form,
                "error_message": str(e),
                "delimiters": Delimiter.objects.all(),
                "timestamps": DateFormat.objects.all(),
            },
        )
    else:
        form = UploadFileForm()
        return render(
            request,
            "conversation_analyst/upload.html",
            {
                "form": form,
                "delimiters": Delimiter.objects.all(),
                "timestamps": DateFormat.objects.all(),
            },
        )


def content_review(request, file_slug):
    # Define the content review view function.
    # Displays detailed analysis of messages within a file.
    # Retrieves messages, analysis, persons, locations, risk words, and chat conversations associated with the file.
    # Generates Google Maps URLs for locations.

    try:
        file = File.objects.get(slug=file_slug)
        messages = Message.objects.filter(file=file)
        for message in messages:
            message.set_main_sender(messages[0].sender)
        analysis = Analysis.objects.get(file=file)
        persons = Person.objects.filter(analysis=analysis)
        locations = Location.objects.filter(analysis=analysis)
        risk_words = RiskWordResult.objects.filter(analysis=analysis)
        vis_path = VisFile.objects.filter(analysis=analysis)[0]
        chats = ChatGPTConvo.objects.filter(file=file)

        # Create Google Maps URLs for each location
        base_url = "https://www.google.com/maps/search/?api=1&query=$"
        locations_with_urls = []
        for location in locations:
            full_url = f"{base_url}{location.name}"
            locations_with_urls.append({"name": location.name, "url": full_url})
        context_dict = {
            "messages": messages,
            "persons": persons,
            "locations": locations,
            "risk_words": risk_words,
            "vis_path": vis_path.file_path,
            "URL": locations_with_urls,
            "file": file,
            "chats": chats,
        }

        return render(
            request, "conversation_analyst/content_review.html", context=context_dict
        )

    except File.DoesNotExist:
        return HttpResponse("File not exist")
    except Analysis.DoesNotExist:
        return HttpResponse("Analysis not exist")


def filter_view(request):
    # Define the filter view function.
    # Handles AJAX requests for filtering messages.
    # Filters messages based on provided parameters such as date range, keywords, and risk ratings.
    # Returns JSON response with filtered message data.

    filters = request.GET.get("filters", "[]")
    filters = json.loads(filters)
    file_slug = request.GET["file_slug"]
    start_date = request.GET.get("startDate")
    end_date = request.GET.get("endDate")
    risk = request.GET.get("risk", "[]")
    risk = json.loads(risk)

    try:
        file = File.objects.get(slug=file_slug)
        filter_params = {"file": file}
        if start_date:
            filter_params["timestamp__gte"] = datetime.strptime(
                start_date, "%Y-%m-%dT%H:%M"
            )
        if end_date:
            filter_params["timestamp__lte"] = datetime.strptime(
                end_date, "%Y-%m-%dT%H:%M"
            )

        messages = Message.objects.filter(**filter_params)
        analysis = Analysis.objects.get(file=file)
        persons = Person.objects.filter(analysis=analysis)
        locations = Location.objects.filter(analysis=analysis)
        risk_words = RiskWordResult.objects.filter(analysis=analysis)
        if len(filters) > 0:
            filter_condition = Q()
            for word in filters:
                search_term = r"(?<![a-zA-Z0-9]){}(?![a-zA-Z0-9])".format(word)
                filter_condition |= Q(tags__iregex=search_term)
            messages = messages.filter(filter_condition)

        if len(risk) > 0:
            filter_condition = Q()
            for risk_number in risk:
                filter_condition |= Q(risk_rating=risk_number)
            messages = messages.filter(filter_condition)
    except Exception as e:
        print(e)
        return JsonResponse(
            {"result": "error", "message": f"Internal Server Error with error: {e}"}
        )
    return JsonResponse(
        {
            "results": render_to_string(
                "conversation_analyst/messages.html",
                {
                    "messages": messages,
                    "persons": persons,
                    "locations": locations,
                    "risk_words": risk_words,
                },
            )
        }
    )


def settings_page(request):
    # Define the settings page view function.
    # Retrieves keyword suites and associated risk words.
    # Renders the settings page with keyword suites and risk words.
    tab = request.GET.get("tab", "default")
    if tab == "threshold":
        context_dict = {}
        obj, created = CustomThresholds.objects.get_or_create(id=1)
        if created:
            context_dict["strictness_default"] = 2
            context_dict["sentiment_default"] = 2
        else:
            context_dict["strictness_default"] = obj.strictness_level
            context_dict["sentiment_default"] = obj.sentiment_level
        return render(
            request, "conversation_analyst/strictness.html", context=context_dict
        )
    else:
        keyword_suites = KeywordSuite.objects.all()
        if len(keyword_suites) == 0:
            context_dict = {}
        else:
            suite = keyword_suites[0]
            risk_words = RiskWord.objects.filter(suite=suite)
            context_dict = {"keyword_suites": keyword_suites, "risk_words": risk_words}
        if tab == "default":
            return render(
                request, "conversation_analyst/settings.html", context=context_dict
            )
        else:
            return render(
                request, "conversation_analyst/setting_tab.html", context=context_dict
            )


def strictness_update(request):
    if request.method == "POST":
        attr = request.POST["attr"]
        level = int(request.POST["level"])
        obj = CustomThresholds.objects.get_or_create(id=1)[0]
        if attr == "strictness":
            obj.strictness_level = level
            match level:
                case 0:
                    obj.word_risk = 10
                    obj.max_risk = float("inf")
                    obj.average_risk = float("inf")
                case 1:
                    obj.word_risk = 8
                    obj.max_risk = 50
                    obj.average_risk = 1
                case 2:
                    obj.word_risk = 7
                    obj.max_risk = 40
                    obj.average_risk = 0.8
                case 3:
                    obj.word_risk = 6
                    obj.max_risk = 30
                    obj.average_risk = 0.8
                case _:
                    print("Invalid strictness level")
        else:
            obj.sentiment_level = level
            match level:
                case 0:
                    obj.sentiment_multiplier = 0
                case 1:
                    obj.sentiment_multiplier = 0.2
                case 2:
                    obj.sentiment_multiplier = 0.5
                case 3:
                    obj.sentiment_multiplier = 0.8
                case _:
                    print("Invalid sentiment level")
        obj.save()
        return HttpResponse(f"attribute {attr} has been updated to level {level}")


def create_suite(request):
    # Define the create suite view function.
    # Handles POST request to create a new keyword suite.
    # Validates uniqueness of suite name and adds it to the database.
    # Returns JSON response indicating success or failure.

    if request.method == "POST":
        try:
            suite_name = request.POST["name"]
            suite_obj = KeywordSuite.objects.create(name=suite_name)
            suite_obj.default = True
            suite_obj.save()
            context_dict = {"message": "New suite added", "suiteId": suite_obj.id}
            return JsonResponse(context_dict, status=201)
        except IntegrityError as e:
            # print(e)
            return JsonResponse(
                {"message": f"Suite name has to be unique with error: {e}"}, status=500
            )


def delete_suite(request):
    # Define the delete suite view function.
    # Handles GET request to delete a keyword suite.
    # Deletes associated risk words and the suite itself.
    # Returns HTTP response indicating success.

    if request.method == "GET":
        suite_id = request.GET["suiteId"]
        suite_obj = KeywordSuite.objects.get(id=suite_id)
        RiskWord.objects.filter(suite=suite_obj).delete()
        suite_obj.delete()
        return HttpResponse("suite deleted")


def select_suite(request):
    # Define the select suite view function.
    # Handles GET request to retrieve keywords associated with a keyword suite.
    # Serializes keyword objects and returns JSON response.

    if request.method == "GET":
        suite_name = request.GET["suite"].strip()
        suite = KeywordSuite.objects.get(name=suite_name)
        keywords = RiskWord.objects.filter(suite=suite)
        # field_values_1 = [obj.your_field for obj in your_objects_queryset]
        serialized_keywords = serialize("json", keywords)
        return JsonResponse({"objects": serialized_keywords}, safe=False)


def create_keyword(request):
    # Define the create keyword view function.
    # Handles POST request to create a new keyword within a suite.
    # Creates a new RiskWord object and associates it with the specified suite.
    # Returns JSON response indicating success.

    if request.method == "POST":
        keyword = request.POST["keyword"]
        suite_name = request.POST["suite"].strip()
        risk = request.POST["risk"]
        suite = KeywordSuite.objects.get(name=suite_name)
        keyword_obj = RiskWord.objects.create(
            suite=suite, keyword=keyword, risk_factor=risk
        )
        keyword_obj.save()

        context_dict = {"message": "New keyword added", "keywordId": keyword_obj.id}
        return JsonResponse(context_dict)


def delete_keyword(request):
    # Define the delete keyword view function.
    # Handles GET request to delete a keyword.
    # Deletes the specified keyword object.
    # Returns HTTP response indicating success.

    if request.method == "GET":
        keyword_id = request.GET["keywordId"]
        RiskWord.objects.get(id=keyword_id).delete()
        return HttpResponse("keyword deleted")


def check_suite(request):
    # Define the check suite view function.
    # Handles POST request to check/uncheck a keyword suite for a specific plan.
    # Modifies keyword suite's plan association based on checkbox status.
    # Returns HTTP response with status and message.

    if request.method == "POST":
        suite_id = request.POST["suiteId"]
        isChecked = json.loads(request.POST["value"])
        suite = KeywordSuite.objects.get(id=suite_id)
        suite.default = isChecked
        suite.save()

        return HttpResponse(
            suite.name + " is now included")


def risk_update(request):
    # Define the check suite view function.
    # Handles POST request to check/uncheck a keyword suite for a specific plan.
    # Modifies keyword suite's plan association based on checkbox status.
    # Returns HTTP response with status and message.

    if request.method == "POST":
        keywordId = request.POST["keyword"]
        risk = int(request.POST["risk"])
        keyword_obj = RiskWord.objects.filter(id=keywordId).first()
        keyword_obj.risk_factor = risk
        keyword_obj.save()

        return HttpResponse(
            "risk factor of " + keyword_obj.keyword + " is updated to " + str(keyword_obj.risk_factor)
        )


def gpt_switch(request):
    # Define the gpt switch view function.
    # Handle POST request to toggle GPT switch.
    # Modifies the boolean field for GPT switch
    # Returns HttpResponse indicating success or failure of the switch toggle.
    if request.method == "POST":
        try:
            isChecked = json.loads(request.POST["value"])
            switch, created = GptSwitch.objects.get_or_create(id=1)
            switch.on = isChecked
            switch.save()
            if created:
                return HttpResponse(f"gpt switched created, on: {isChecked}")
            else:
                return HttpResponse(f"switch on: {isChecked}")

        except KeyError as e:
            return HttpResponse(f"{e}")


def rename_file(request):
    # Define the rename file view function.
    # Handles POST request to rename a file.
    # Modifies the title of the specified file.
    # Returns JSON response indicating success or failure.

    if request.method == "POST":
        try:
            newTitle = request.POST["fileName"]
            fileId = request.POST["fileId"]
            file_obj = File.objects.filter(id=fileId).first()
            fullTitle = newTitle + "." + file_obj.format
            file_obj.title = fullTitle
            file_obj.save()

            context_dict = {
                "message": "file name of file "
                + str(file_obj.id)
                + " is updated to "
                + fullTitle,
                "fileName": fullTitle,
            }
            return JsonResponse(context_dict)

        except Exception as e:
            print(e)
            return JsonResponse({"message": f"with error: {e}"})


def delete_file(request):
    # Define the delete file view function.
    # Handles POST request to delete a file.
    # Remove the file object from database.
    # Returns HTTPresponse indicating success or failure.

    if request.method == "POST":
        try:
            fileId = request.POST["fileId"]
            file_obj = File.objects.get(id=fileId)
            file_obj.delete()
            return HttpResponse(f"file {fileId} has been successfully deleted")

        except File.DoesNotExist:
            return HttpResponse(f"file with id {fileId} doesn't exist")


def export_view(request, file_slug):
    # Define the export view function.
    # Handles GET request to export file data in XML format.
    # Retrieves file data and serializes it into XML format.
    # Returns HTTP response with XML data for download.

    file = File.objects.get(slug=file_slug)
    messages = Message.objects.filter(file=file)
    analysis = Analysis.objects.get(file=file)
    persons = Person.objects.filter(analysis=analysis)
    locations = Location.objects.filter(analysis=analysis)
    risk_words = RiskWordResult.objects.filter(analysis=analysis)

    root = Element("exported_data")

    persons_element = SubElement(root, "persons")
    for person in persons:
        entry_element = SubElement(persons_element, "person")
        SubElement(entry_element, "name").text = person.name

    locations_element = SubElement(root, "locations")
    for location in locations:
        entry_element = SubElement(locations_element, "location")
        SubElement(entry_element, "name").text = location.name

    risk_words_element = SubElement(root, "risk_words")
    for risk_word in risk_words:
        entry_element = SubElement(risk_words_element, "risk_word")
        SubElement(entry_element, "keyword").text = risk_word.riskword.keyword
        SubElement(entry_element, "risk_factor").text = str(risk_word.risk_factor)
        SubElement(entry_element, "amount").text = str(risk_word.amount)

    messages_element = SubElement(root, "messages")
    for message in messages:
        entry_element = SubElement(messages_element, "message")
        SubElement(entry_element, "timestamp").text = str(message.timestamp)
        SubElement(entry_element, "sender").text = message.sender
        SubElement(entry_element, "content").text = message.content
        SubElement(entry_element, "display_content").text = message.display_content
        SubElement(entry_element, "risk_level").text = str(message.risk_rating)
    xml_data = minidom.parseString(tostring(root)).toprettyxml(indent="  ")

    response = HttpResponse(xml_data, content_type="application/xml")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{file_slug}_exported_data.xml"'
    return response


def quick_chat_message(request):
    # Define the quick chat message view function.
    # Handles GET request to generate quick chat response.
    # Uses OpenAI GPT-3.5 to generate responses based on provided message.
    # Returns JSON response with generated chat response.

    file_slug = request.GET["file_slug"]
    try:
        file = File.objects.get(slug=file_slug)
        messages = Message.objects.filter(file=file)
        system_message = "Here is an extract of a set of messages, please sumerise the messages. They are formatted of the messages will be'<Timestamp>: <Name>: <Message> \n"
        for message in messages:
            system_message += (
                f"{message.timestamp}: {message.sender}:  {message.content} \n"
            )
        client = OpenAI(
            api_key=os.environ.get("CHATGPT_API_KEY"),
        )
        conversation_history = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": "please sumerise the messages"},
        ]

        response = client.chat.completions.create(
            model=os.environ.get("CHATGPT_VERSION"), messages=[*conversation_history]
        )

        reply = response.choices[0].message.content
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/quick_chat_result.html",
                    {"response": reply},
                )
            }
        )

    except openai.APIError as e:
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/quick_chat_result.html",
                    {"response": f"OpenAI API returned an API Error: {e}"},
                )
            }
        )
    except openai.APIConnectionError as e:
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/quick_chat_result.html",
                    {"response": f"Failed to connect to OpenAI API: {e}"},
                )
            }
        )
    except openai.RateLimitError as e:
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/quick_chat_result.html",
                    {"response": f"OpenAI API request exceeded rate limit: {e}"},
                )
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/quick_chat_result.html",
                    {"response": f"An error occurred: {e}"},
                )
            }
        )


def chatgpt_new_message(request):
    # Define the chatgpt new message view function.
    # Handles GET request to create a new chat conversation.
    # Creates a new chat conversation associated with the specified file.
    # Returns JSON response with URL to the created conversation.

    file_slug = request.GET["file_slug"]
    start_date = request.GET.get("startDate")
    end_date = request.GET.get("endDate")
    try:
        file = File.objects.get(slug=file_slug)

        convo = ChatGPTConvo.objects.create(file=file)
        convo.init_save()
        filter_params = {"file": file}
        if start_date:
            convo.start = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
            filter_params["timestamp__gte"] = datetime.strptime(
                start_date, "%Y-%m-%dT%H:%M"
            )
        if end_date:
            convo.end = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
            filter_params["timestamp__lte"] = datetime.strptime(
                end_date, "%Y-%m-%dT%H:%M"
            )
        messages = Message.objects.filter(**filter_params)
        convo.save()

        system_message = "You are answering questions about a some text messages with lots of detail, the formated of the messages will be'<Timestamp>: <Name>: <Message> \n"
        for message in messages:
            system_message += (
                f"{message.timestamp}: {message.sender}:  {message.content} \n"
            )

        add_chat_message("system", system_message, convo)
        return JsonResponse({"url": convo.slug})

    except Exception as e:
        print(e)
        return JsonResponse(
            {"result": "error", "message": f"Internal Server Error with error: {e}"}
        )


def chatgpt_page(request, chatgpt_slug):
    # Define the chatgpt page view function.
    # Handles GET request to display chat conversation page.
    # Retrieves messages, persons, locations, and risks associated with the conversation.
    # Renders the chat conversation page with associated data.
    chats = ChatGPTConvo.objects.order_by("-date")
    convo = ChatGPTConvo.objects.get(slug=chatgpt_slug)
    analysis = Analysis.objects.get(file=convo.file)
    person_words = Person.objects.filter(analysis=analysis)
    location_words = Location.objects.filter(analysis=analysis)
    risk_words = RiskWordResult.objects.filter(analysis=analysis)
    messages = ChatGPTMessage.objects.filter(convo=convo)
    persons, locations, risks = [], [], []
    for person in person_words:
        p, fd = add_chat_filter(person.name, "person", convo)
        persons.append(p)
    for location in location_words:
        l, fd = add_chat_filter(location.name, "location", convo)
        locations.append(l)
    for risk_word in risk_words:
        r, fd = add_chat_filter(risk_word.riskword.keyword, "risk", convo)
        risks.append(r)

    return render(
        request,
        "conversation_analyst/chatgpt.html",
        {
            "chats": chats,
            "convo": convo,
            "messages": messages,
            "persons": persons,
            "locations": locations,
            "risks": risks,
        },
    )


def chatgpt_page_without_slug(request):
    # Define the chatgpt page without slug view function.
    # Handles GET request to display chat conversation page without a specific conversation.
    # Retrieves and renders all available chat conversations.

    chats = ChatGPTConvo.objects.order_by("-date")
    return render(request, "conversation_analyst/chatgpt.html", {"chats": chats, "empty": True})


def message(request):
    # Define the message view function.
    # Handles GET request to process user input in chat conversation.
    # Uses OpenAI GPT-3.5 to generate responses based on conversation history and user input.
    # Returns JSON response with updated conversation messages.

    chatgpt_slug = request.GET["chatgpt_slug"]
    convo = ChatGPTConvo.objects.get(slug=chatgpt_slug)
    messages = ChatGPTMessage.objects.filter(convo=convo)
    try:
        message_content = request.GET["message_content"]
        messages = ChatGPTMessage.objects.filter(convo=convo)
        conversation_history = []
        for message in messages:
            conversation_history.append(
                {"role": message.typeOfMessage, "content": message.content}
            )

        client = OpenAI(
            api_key=os.environ.get("CHATGPT_API_KEY"),
        )

        conversation_history.append({"role": "user", "content": message_content})

        response = client.chat.completions.create(
            model=os.environ.get("CHATGPT_VERSION"), messages=[*conversation_history]
        )

        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})
        add_chat_message("user", message_content, convo)
        add_chat_message("assistant", reply, convo)

        messages = ChatGPTMessage.objects.filter(convo=convo)
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/chatgpt_messages.html",
                    {"convo": convo, "messages": messages},
                )
            }
        )
    except openai.APIError as e:
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/chatgpt_messages.html",
                    {
                        "convo": convo,
                        "messages": messages,
                        "error": f"OpenAI API returned an API Error: {e}",
                    },
                )
            }
        )
    except openai.APIConnectionError as e:
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/chatgpt_messages.html",
                    {
                        "convo": convo,
                        "messages": messages,
                        "error": f"Failed to connect to OpenAI API: {e}",
                    },
                )
            }
        )
    except openai.RateLimitError as e:
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/chatgpt_messages.html",
                    {
                        "convo": convo,
                        "messages": messages,
                        "error": f"OpenAI API request exceeded rate limit: {e}",
                    },
                )
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/chatgpt_messages.html",
                    {
                        "convo": convo,
                        "messages": messages,
                        "error": f"An error occurred: {e}",
                    },
                )
            }
        )


def settings_delim(request):
    # Define the settings delim view function.
    # Handles GET request to display settings for delimiters.
    # Retrieves all delimiters from the database.
    # Renders the settings page with delimiter options.

    delims = Delimiter.objects.all()

    context_dict = {"delimiters": delims}
    return render(
        request, "conversation_analyst/settings_delim.html", context=context_dict
    )


def initialise_delim(delim_name, delim_value, order_value, default=False):
    # Define the initialise delim view function.
    # It creates the delimitors in the database
    # returns a delimiter object.
    new_obj = Delimiter.objects.create(
        name=delim_name, value=delim_value, order=order_value, is_default=default
    )
    new_obj.save()
    return new_obj


def create_delimiter(request):
    # Define the create delimiter view function.
    # Handles POST request to create a new delimiter.
    # Creates a new delimiter object and adds it to the database.
    # Returns JSON response indicating success or failure.

    if request.method == "POST":
        try:
            delim_name = request.POST["name"]
            delim_value = request.POST["value"]
            delim_order = request.POST["order"]
            delim_obj = initialise_delim(delim_name, delim_value, delim_order)
            context_dict = {"message": "New delimiter added", "delimId": delim_obj.id}
            return JsonResponse(context_dict, status=201)
        except IntegrityError as e:
            return JsonResponse(
                {"message": f"Delimiter has to be unique with error: {e}"}, status=500
            )


def delete_delimiter(request):
    # Define the delete delimiter view function.
    # Handles GET request to delete a delimiter.
    # Deletes the specified delimiter object.
    # Returns HTTP response indicating success.

    if request.method == "GET":
        delim_id = request.GET["delimId"]
        Delimiter.objects.get(id=delim_id).delete()
        return HttpResponse("Delimiter deleted")


def order_update(request):
    # Define the order update view function.
    # Handles POST request to update the order of a delimiter.
    # Modifies the order value of the specified delimiter.
    # Returns HTTP response indicating success.

    if request.method == "POST":
        delimId = request.POST["delim"]
        order = int(request.POST["order"])
        delim_obj = Delimiter.objects.filter(id=delimId).first()
        delim_obj.order = order
        delim_obj.save()

        return HttpResponse(
            "Order of " + delim_obj.name + " is updated to " + str(order)
        )


def value_update(request):
    # Define the value update view function.
    # Handles POST request to update the value of a delimiter.
    # Modifies the value of the specified delimiter.
    # Returns HTTP response indicating success.

    if request.method == "POST":
        delimId = request.POST["delim"]
        value = request.POST["value"]
        delim_obj = Delimiter.objects.filter(id=delimId).first()
        delim_obj.value = value
        delim_obj.save()

        return HttpResponse(
            "Value of " + delim_obj.name + " is updated to " + str(value)
        )


def suite_selection(request, file_slug):
    # Define the suite selection view function.
    # Handles GET request to select a keyword suite for analysis.
    # Retrieves available keyword suites.
    # Renders the suite selection page with options to choose a suite.

    if request.method == "GET":
        keyword_suites = KeywordSuite.objects.all()
        gpt_switch = GptSwitch.objects.get(id=1)
        if len(keyword_suites) == 0:
            context_dict = {}
        else:
            suite = keyword_suites[0]
            risk_words = RiskWord.objects.filter(suite=suite)
            context_dict = {"keyword_suites": keyword_suites, "risk_words": risk_words}

        context_dict["file_slug"] = file_slug
        context_dict["gpt_switch"] = gpt_switch.on
        return render(
            request, "conversation_analyst/suite_selection.html", context=context_dict
        )

    else:
        keyword_suites = KeywordSuite.objects.filter(default=True)
        keywords = RiskWord.objects.filter(suite__in=keyword_suites)

        try:
            file_obj = File.objects.get(slug=file_slug)
            messages = Message.objects.filter(file=file_obj)
            threshold = CustomThresholds.objects.all()[0]
            gpt_switch = GptSwitch.objects.get(id=1).on
            process_file(file_obj, keywords, messages, threshold, gpt_switch)
            return HttpResponseRedirect(
                reverse("content_review", kwargs={"file_slug": file_obj.slug})
            )
        except File.DoesNotExist:
            return HttpResponse("File object doesn't exist")
        except Exception as e:
            return HttpResponse(f"Error while processing file, {e}")


def clear_duplicate_submission(request):
    # Define the clear duplicate submission view function.
    # Handles GET request to clear duplicate file submissions.
    # Deletes the specified file if no associated analysis exists.
    # Returns HTTP response indicating success.

    if request.method == "GET":
        try:
            file_slug = request.GET["file_slug"]
            file_obj = File.objects.get(slug=file_slug)
            if not Analysis.objects.filter(file=file_obj).exists():
                file_obj.delete()
                return HttpResponse("File deleted")
            else:
                return HttpResponse("File kept")
        except Exception as e:
            print(f"exception: {e}")
            return HttpResponse("An error occured while trying to delete the file")


def search_chats(request):
    # Define the search chats view function.
    # Handles GET request to search chat conversations.
    # Filters chat conversations based on provided query.
    # Returns JSON response with filtered chat conversations.

    chats = ChatGPTConvo.objects.order_by("-date")
    page_slug = request.GET["page_slug"]
    query = request.GET["query"]
    if len(page_slug) > 0 and page_slug.strip() != "":
        convo = ChatGPTConvo.objects.get(slug=page_slug)
        if len(query) > 0 and query.strip() != "":
            chats = chats.filter(title__icontains=query)
        return JsonResponse(
            {
                "results": render_to_string(
                    "conversation_analyst/chats.html",
                    {"convo": convo, "chats": chats},
                )
            }
        )
    if len(query) > 0 and query.strip() != "":
        chats = chats.filter(title__icontains=query)
    return JsonResponse(
        {
            "results": render_to_string(
                "conversation_analyst/chats.html",
                {"chats": chats},
            )
        }
    )


def rename_chat(request):
    # Define the rename chat view function.
    # Handles POST request to rename a chat.
    # Modifies the title of the specified chat.
    # Returns JSON response indicating success or failure.

    if request.method == "POST":
        try:
            newTitle = request.POST["chatName"]
            chatId = request.POST["chatId"]
            chat_obj = ChatGPTConvo.objects.filter(id=chatId).first()
            chat_obj.title = newTitle
            chat_obj.save()

            context_dict = {
                "message": "file name of file "
                + str(chat_obj.id)
                + " is updated to "
                + newTitle,
                "chatName": newTitle,
            }
            return JsonResponse(context_dict)

        except Exception as e:
            print(e)
            return JsonResponse({"message": f"with error: {e}"})
