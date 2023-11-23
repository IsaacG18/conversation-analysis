from .Keywords import *
import spacy
import numpy as np
nlp = spacy.load("en_core_web_sm")


def tag_text(text, keywords):
    doc = nlp(text)
    return doc, [(token.text, keywords.get_keyword(token.text)["risk"] if token.text in keywords.get_keywords() else 0, keywords.get_keyword_topics(token.text) if token.text in keywords.get_keywords() else None) for token in doc]

def get_top_n_risk_keywords(tagged_tokens, n):
    token_risk = {}
    token_count = {}
    for token, risk, topics in tagged_tokens:
        if risk != 0:
            if token not in token_risk:
                token_risk[token] = risk
            if token in token_count:
                token_count[token] += 1
            else:
                token_count[token] = 1
    
    sorted_tokens = sorted(token_risk, key=lambda x: token_risk[x], reverse=True)[:n]
    result = [(token, token_risk[token], token_count[token]) for token in sorted_tokens]
    return result

def get_top_n_common_topics_with_avg_risk(tagged_tokens, n):
    topics_count = {}
    risk_factors = {}
    for token, risk, topics in tagged_tokens:
        if topics is not None:
            for topic in topics:
                if topic in topics_count:
                    topics_count[topic] += 1
                else:
                    topics_count[topic] = 1
                if topic in risk_factors:
                    risk_factors[topic] += risk
                else:
                    risk_factors[topic] = risk
    sorted_topics = sorted(topics_count, key=topics_count.get)
    avg_risk_factors = []
    for topic in reversed(sorted_topics):
        avg_risk_factors.append([topic,topics_count[topic],risk_factors[topic]/topics_count[topic]])
    return avg_risk_factors


def get_date_messages(parsed_data):
    # Dictionary to store arrays for each person
    person_arrays = {}

    for entry in parsed_data:
        sender_name = entry.get('Sender', None)
        message_length = len(entry.get('Message', ''))

        if sender_name is not None:
            if sender_name not in person_arrays:
                person_arrays[sender_name] = {'timestamps': [], 'message_lengths': []}

            person_arrays[sender_name]['timestamps'].append(entry.get('Timestamp', ''))
            person_arrays[sender_name]['message_lengths'].append(message_length)

    # Convert the lists to NumPy arrays
    for person, data in person_arrays.items():
        data['timestamps'] = np.array(data['timestamps'])
        data['message_lengths'] = np.array(data['message_lengths'])

    return person_arrays

def extract(doc, labels):
    found_entities = {label: [] for label in labels}
    
    for entity in doc.ents:
        if entity.label_ in labels:
            found_entities[entity.label_].append(entity.text)
    return found_entities

def message_to_text(list_of_messages):
    text = ""
    for message in list_of_messages:
        text += message.get("Message", "") + " "
    return text

def create_arrays(parsed_data):
    # Dictionary to store arrays for each person
    person_arrays = {}

    for entry in parsed_data:
        sender_name = entry.get('Sender', None)
        message_length = len(entry.get('Message', ''))

        if sender_name is not None:
            if sender_name not in person_arrays:
                person_arrays[sender_name] = {'timestamps': [], 'message_lengths': []}

            person_arrays[sender_name]['timestamps'].append(entry.get('Timestamp', ''))
            person_arrays[sender_name]['message_lengths'].append(message_length)

    # Convert the lists to NumPy arrays
    for person, data in person_arrays.items():
        data['timestamps'] = np.array(data['timestamps'])
        data['message_lengths'] = np.array(data['message_lengths'])

    return person_arrays