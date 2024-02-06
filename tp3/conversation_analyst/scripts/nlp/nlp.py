from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
import numpy as np
import re
nlp = spacy.load("en_core_web_md")
AVERAGE_RISK = 0.8
MAX_RISK = 40
SENTIMENT_DIVIDER = 2
RISK_LEVELS = 2



def classify(text):
    return text.replace(' ', '_')

def label_entity(entity):
    start_tag = f'<span class="{classify(entity.label_)} {classify(entity.text)}">'
    end_tag = '</span>'
    offset = len(start_tag) + len(end_tag)
    return start_tag + entity.text + end_tag, offset

def label_keyword(keyword, root):
    start_tag = f'<span class="{classify(root)} risk">'
    end_tag = '</span>'
    offset = len(start_tag) + len(end_tag)
    return start_tag + keyword + end_tag, offset

def tag_text(messages, keywords, labels):
    analyzer = SentimentIntensityAnalyzer()
    found_entities = {label: [] for label in labels}
    for message in messages:
        distance = 0
        message["Display_Message"] = message["Message"]
        message["risk"] = 0
        message['entities'] = []
        risk_total = 0
        message["doc"] = nlp(message["Message"])
        sentiment = analyzer.polarity_scores(message["Message"])['compound']
        tag_list = []
        for label in labels:
            message[label] = 0
        for entity in message["doc"].ents:
            if entity.label_ in labels:
                labeled, offset = label_entity(entity)
                found_entities[entity.label_].append((entity.text))
                message["Display_Message"] = message["Display_Message"][:entity.start_char + distance] + labeled + message["Display_Message"][entity.end_char+ distance:]
                distance += offset
                message[entity.label_] += 1
                message['entities'].append(entity.text)
        ptr = 0
        for token in message["doc"]:
            token_text = token.text
            word_regex = re.compile(r'(?<![a-zA-Z0-9]){}(?![a-zA-Z0-9])'.format(re.escape(token_text)))
            
            if (keyword := keywords.filter(lemma=token.lemma_).first()) is not None:
                risk = keyword.risk_factor * (1 + abs(sentiment)/SENTIMENT_DIVIDER)
                topics = keyword.topics.all()
                risk_total += risk
                if risk >7:
                    message["risk"] += 1
                    
                labeled, offset = label_keyword(token_text, keyword.keyword)
                
                match = word_regex.search(message["Display_Message"], ptr)
                if match:
                    start = match.start()
                    ptr = match.end()+offset
                    message["Display_Message"] = message["Display_Message"][:start] + labeled + message["Display_Message"][start + len(token_text):]
                    tag_list.append((keyword.keyword, risk, topics))
                    message['entities'].append(keyword.keyword)
    
        if risk_total > 40:
            message["risk"] += 1
        if risk_total/len(message["Message"].split()) >AVERAGE_RISK:
            message["risk"] += 1
        if message["risk"] > RISK_LEVELS:
            message["risk"]=RISK_LEVELS
            
        message["tags"] = tag_list
    return messages, found_entities

def get_top_n_risk_keywords(messages, n):
    token_risk = {}
    token_count = {}
    for message in messages:
        for keyword, risk, topics in message["tags"]:
            if risk != 0:
                if keyword not in token_risk:
                    token_risk[keyword] = risk
                if keyword in token_count:
                    token_count[keyword] += 1
                else:
                    token_count[keyword] = 1
    
    sorted_tokens = sorted(token_risk, key=lambda x: token_risk[x], reverse=True)[:n]
    result = [(token, token_risk[token], token_count[token]) for token in sorted_tokens]
    return result

def get_top_n_common_topics_with_avg_risk(messages, n):
    topics_count = {}
    risk_factors = {}
    for message in messages:
        for token, risk, topics in message["tags"]:
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


def message_to_text(list_of_messages):
    text = ""
    for message in list_of_messages:
        text += message.get("Message", "") + " "
    return text ,list_of_messages

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

def get_keyword_lamma(keyword):
    doc = nlp(keyword)
    lemmas = [token.lemma_ for token in doc]
    return " ".join(lemmas)

