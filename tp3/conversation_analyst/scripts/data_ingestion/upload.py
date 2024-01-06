from django.conf import settings
from ingestion import parse_chat_file
import sys
import os

from tp3.conversation_analyst.scripts.data_ingestion import ingestion
from tp3.conversation_analyst.views import generate_analysis_objects

from ..nlp.nlp import *
from ..nlp.Keywords import *

# sys.path.append(r'C:/Users/fmitc/Documents/3rd Year/Professional Software Development/Project/branch 53/cs39_main/tp3/tp3/scripts/nlp')
#
class InvalidDelimitersException(Exception):
    pass

def process_file(file, delimiters=[["Timestamp", ","], ["Sender", ":"]], keywords=Keywords()):
    directory = os.path.join(settings.MEDIA_ROOT, 'uploads')
    file_path = os.path.join(directory, file.title)

    # Read the first few lines of the document to determine the actual delimiters
    try:
        with open(file_path, 'r') as file:
            sample_lines = [next(file) for _ in range(10)]
    except Exception as e:
        raise Exception(f"Error reading the file: {e}")

    # Determine the actual delimiters based on the sample lines
    actual_delimiters = []
    for line in sample_lines:
        for delimiter in delimiters:
            if delimiter[1] in line:
                actual_delimiters.append(delimiter[1])

    if set(actual_delimiters) != set([d[1] for d in delimiters]):
        raise InvalidDelimitersException("Selected delimiters do not match the actual delimiters in the document.")
        #TODO: exception should display in ui

    chat_messages = ingestion.parse_chat_file(file_path, delimiters)
    message_count = create_arrays(chat_messages)
    nlp_text, person_and_locations = tag_text(chat_messages, keywords, ["PERSON", "GPE"])
    risk_words = get_top_n_risk_keywords(nlp_text, 3)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)
    generate_analysis_objects(file, chat_messages, message_count, person_and_locations, risk_words, common_topics)