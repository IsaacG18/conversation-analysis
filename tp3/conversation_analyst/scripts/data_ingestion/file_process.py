from ..nlp.nlp import create_arrays, get_top_n_risk_keywords, get_top_n_common_topics_with_avg_risk, tag_text
from .. import object_creators
from . import ingestion, plotter
from django.conf import settings
import os


def parse_file(file, date_formats, delimiters=[["Timestamp", ","], ["Sender", ":"]]):
    if not file.title.endswith((".docx", ".txt", ".csv")):
        raise ValueError(
            "Unsupported file type. Only .txt, .csv and .docx are supported."
        )

    messages = ingestion.parse_chat_file(file.file.path, delimiters, date_formats)
    generate_message_objects(file, messages)


def process_file(file, keywords, messages, threshold):
    chat_messages = [
        {
            "Timestamp": message.timestamp,
            "Sender": message.sender,
            "Message": message.content,
            "ObjectId": message.id,
        }
        for message in messages
    ]
    message_count = create_arrays(chat_messages)
    nlp_text, person_and_locations = tag_text(
        chat_messages,
        keywords,
        ["PERSON", "GPE"],
        threshold.average_risk,
        threshold.sentiment_divider,
        threshold.max_risk,
        threshold.word_risk
    )
    risk_words = get_top_n_risk_keywords(nlp_text, 10)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)
    generate_analysis_objects(
        file,
        chat_messages,
        message_count,
        person_and_locations,
        risk_words,
        common_topics,
    )
    media_root = os.path.join(settings.MEDIA_ROOT, "uploads")
    full_file_path = os.path.join(media_root, file.title)
    if os.path.exists(full_file_path):
        os.remove(full_file_path)


def generate_message_objects(file, chat_messages):
    for message in chat_messages:
        object_creators.add_message(
            file, message["Timestamp"], message["Sender"], message["Message"]
        )


def generate_analysis_objects(
    file, chat_messages, message_count, person_and_locations, risk_words, common_topics
):
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
