from ingestion import parse_chat_file
from nlp.nlp import create_arrays,tag_text,extract,get_top_n_risk_keywords,message_to_text,get_top_n_common_topics_with_avg_risk
from nlp.Keywords import *


def process_file(file_path, delimiters =[["Timestamp", ","], ["Sender", ":"]], keywords = Keywords()):
    chat_messages = parse_chat_file(file_path, delimiters)
    message_count = create_arrays(chat_messages)
    nlp_text = tag_text(message_to_text(chat_messages), keywords)
    person_and_locations = extract(nlp_text, ["PERSON", "GPE"])
    risk_words = get_top_n_risk_keywords(nlp_text, 3)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)
    return message_count,person_and_locations,risk_words,common_topics