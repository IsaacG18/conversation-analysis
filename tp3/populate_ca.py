import os
from os.path import isfile, join

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tp3.settings')
import django

django.setup()

from conversation_analyst.scripts.data_ingestion import ingestion
from conversation_analyst.scripts.nlp.nlp import *
from conversation_analyst.scripts.object_creators import *
from conversation_analyst.views import generate_analysis_objects


def populate():
    sample_dir = os.path.abspath(os.path.join(os.getcwd(), 'static/sample'))
    sample_files = [f for f in os.listdir(sample_dir) if isfile(join(sample_dir, f))]
    for file in sample_files:
        f = add_file(file)
        process_file(f)
        print(f.title + "added to database")


def process_file(file, delimiters=[["Timestamp", ","], ["Sender", ":"]], keywords=Keywords()):
    sample_dir = os.path.abspath(os.path.join(os.getcwd(), 'static/sample'))
    file_path = os.path.join(sample_dir, file.title)
    chat_messages = ingestion.parse_chat_file(file_path, delimiters)
    message_count = create_arrays(chat_messages)
    nlp_text = tag_text(message_to_text(chat_messages), keywords)
    # person_and_locations = extract(nlp_text, ["PERSON", "GPE"])
    person_and_locations = {'PERSON': ['Martin', 'Chris', 'Ma', 'Philly', 'Dune'], 'GPE': ['Philly']}
    risk_words = get_top_n_risk_keywords(nlp_text, 3)
    common_topics = get_top_n_common_topics_with_avg_risk(nlp_text, 3)
    generate_analysis_objects(file, chat_messages, message_count, person_and_locations, risk_words, common_topics)


# Start excution here
if __name__ == '__main__':
    print('Starting population script...')
    populate()
    print('Finished')
