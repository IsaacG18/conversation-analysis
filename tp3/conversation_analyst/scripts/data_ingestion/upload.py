from ingestion import parse_chat_file
import sys
sys.path.append(r'C:/Users/fmitc/Documents/3rd Year/Professional Software Development/Project/branch 53/cs39_main/tp3/tp3/scripts/nlp')


from nlp import *
from Keywords import *


def process_file(file_path, delimiters =[["Timestamp", ","], ["Sender", ":"]], keywords = Keywords()):
    chat_messages = parse_chat_file(file_path, delimiters)
    message_count = create_arrays(chat_messages)
    nlp_text = tag_text(message_to_text(chat_messages), keywords)
    person_and_locations = extract(nlp_text, ["PERSON", "GPE"])
    risk_words = get_top_n_risk_keywords(nlp_text, 3)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)
    return chat_messages, message_count,person_and_locations,risk_words,common_topics