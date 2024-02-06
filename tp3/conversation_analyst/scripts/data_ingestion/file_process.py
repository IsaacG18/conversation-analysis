import sys

from ..nlp.nlp import *
from .. import object_creators
from . import ingestion, plotter

# sys.path.append(r'C:/Users/fmitc/Documents/3rd Year/Professional Software Development/Project/branch 53/cs39_main/tp3/tp3/scripts/nlp')
#


def check_file(file, delimiters=[["Timestamp", ","], ["Sender", ":"]]):

    if not file.title.endswith(('.docx', '.txt', '.csv')):
        raise ValueError("Unsupported file type. Only .txt, .csv and .docx are supported.")

    ingestion.parse_chat_file(file.file.path, delimiters)
    
def process_file(file, keywords, delimiters=[["Timestamp", ","], ["Sender", ":"]]):
    chat_messages = ingestion.parse_chat_file(file.file.path, delimiters)
    message_count = create_arrays(chat_messages)
    nlp_text, person_and_locations = tag_text(chat_messages, keywords, ["PERSON", "GPE"])
    risk_words = get_top_n_risk_keywords(nlp_text, 10)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)
    generate_analysis_objects(file, chat_messages, message_count,person_and_locations,risk_words,common_topics)
    
    
def generate_analysis_objects(file, chat_messages, message_count, person_and_locations, risk_words, common_topics):
    persons = person_and_locations['PERSON']
    locations = person_and_locations['GPE']

    a = object_creators.add_analysis(file)
    for message in chat_messages:
        m = object_creators.add_message(file, message['Timestamp'], message['Sender'], message['Message'], message["Display_Message"], message["entities"],  message["risk"])
    object_creators.add_vis(a, plotter.plots(chat_messages, file.slug, str(a.id)))
    for person in persons:
        p = object_creators.add_person(a, person)
    for location in locations:
        p = object_creators.add_location(a, location)
    for risk_word in risk_words:
        r = object_creators.add_risk_word_result(a, risk_word[0], risk_word[2], risk_word[1])