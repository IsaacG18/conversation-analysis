from ..nlp.nlp import (
    get_top_n_risk_keywords,
    tag_text,
)
from .. import object_creators
from . import ingestion, plotter
from django.conf import settings
import os


def parse_file(file, date_formats, delimiters=[["Timestamp", ","], ["Sender", ":"]], skip=False):
    """
    Arguments:
    file (file): The file object to the user
    date_formats (str): The format of the timestamps in the chat file
    delimiters (list): Is a list of list, with the internal list having it first element be the type and the second being the delimiter
    skip (bool): Test message to skip if it want to move over the first line


    Description:
    This function checkt the file type, ingest the file, then ingests the file, then calls to generate objects for messages
    """

    if not file.title.endswith((".docx", ".txt", ".csv")):
        raise ValueError("Unsupported file type. Only .txt, .csv and .docx are supported.")
    messages = ingestion.parse_chat_file(file.file.path, delimiters, skip, date_formats)
    generate_message_objects(file, messages)


def process_file(file, keywords, messages, threshold, gpt_switch=False):
    """
    Arguments:
    file (file): The file object to the used
    keywords (list): A list of keyword objects
    messages (list): A list of message objects
    threshold (threshold): The threshold object to the used


    Description:
    It coversts messages to a dictionary then start passing them into nlp functions, calls to geneate all the anylsis objects
    Then deletes the uploaded file after all the details have been extracted.
    """
    chat_messages = [
        {
            "Timestamp": message.timestamp,
            "Sender": message.sender,
            "Message": message.content,
            "ObjectId": message.id,
        }
        for message in messages
    ]
    nlp_text, person_and_locations = tag_text(
        chat_messages,
        keywords,
        ["PERSON", "GPE"],
        threshold.average_risk,
        threshold.sentiment_multiplier,
        threshold.max_risk,
        threshold.word_risk,
        gpt_switch
    )
    risk_words = get_top_n_risk_keywords(nlp_text)
    generate_analysis_objects(
        file,
        chat_messages,
        person_and_locations,
        risk_words,
    )
    media_root = os.path.join(settings.MEDIA_ROOT, "uploads")
    full_file_path = os.path.join(media_root, file.title)
    if os.path.exists(full_file_path):
        os.remove(full_file_path)


def generate_message_objects(file, chat_messages):
    """
    Arguments:
    file (file): The file object to the user
    chat_messages (list): A list of a dictionary of objects


    Description:
    This function loops through each message an creates message objects
    """
    for message in chat_messages:
        object_creators.add_message(
            file, message["Timestamp"], message["Sender"], message["Message"]
        )


def generate_analysis_objects(file, chat_messages, person_and_locations, risk_words):
    """
    Arguments:
    file (file): The file object to the user
    chat_messages (list): A list of a message objects
    person_and_locations(dict): A dictionary of two lists one containing all the names and the other locations
    risk_words(list): A list of list which contain details about each risk word

    Description:
    This function loops through each message  and updates it, loops though each person, location, and risk word then adds it to the database
    """
    persons = person_and_locations["PERSON"]
    locations = person_and_locations["GPE"]

    a = object_creators.add_analysis(file)
    for message in chat_messages:
        object_creators.update_message(
            message["ObjectId"],
            message["Display_Message"],
            message["entities"],
            message["risk"],
        )
    object_creators.add_vis(a, plotter.plots(chat_messages, file.slug, str(a.id)))
    for person in persons:
        object_creators.add_person(a, person)
    for location in locations:
        object_creators.add_location(a, location)
    for risk_word in risk_words:
        object_creators.add_risk_word_result(
            a, risk_word[0], risk_word[2], risk_word[1]
        )
