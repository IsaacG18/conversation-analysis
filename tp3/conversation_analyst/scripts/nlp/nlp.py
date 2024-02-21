from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
import numpy as np
import re
import os
from openai import OpenAI

nlp = spacy.load("en_core_web_md")
RISK_LEVELS = 2


def classify(text):
    """
    Arguments:
    text (str): The input text to be classified.

    Returns:
    str: The classified text where spaces are replaced with underscores.

    Description:
    This function replaces spaces in the input text with underscores. This is to allow it be html class
    """
    return text.replace(" ", "_")


def label_entity(label, text):
    """
    Arguments:
    label (str): A entity label.
    text (str): A entity text.

    Returns:
    lable text (str): HTML containing the label text surrounded by spans
    offset(int): How far the text has been offset by

    Description:
    This function generates HTML tags to label the given entity within a text.
    """
    start_tag = f'<span class="{classify(label)} {classify(text)}">'
    end_tag = "</span>"
    offset = len(start_tag) + len(end_tag)
    return start_tag + text + end_tag, offset


def label_keyword(keyword, root):
    """
    Arguments:
    keyword (str): The keyword to be labeled.
    root (str): The root associated with the keyword.

    Returns:
    tagged text (str): HTML containing the keyword text surrounded by spans
    offset(int): How far the text has been offset by

    Description:
    This function generates HTML tags to label the given keyword within a text.
    """
    start_tag = f'<span class="{classify(root)} risk">'
    end_tag = "</span>"
    offset = len(start_tag) + len(end_tag)
    return start_tag + keyword + end_tag, offset


def tag_text(messages, keywords, labels, average_risk=0.8, sentiment_divider=2, max_risk=40, word_risk=7, chatgpt=False):
    """
    Arguments:
    messages (dictionary): A dictionary of messages to be tagged.
    keywords (list): A list of keywords.
    labels (list): A list of labels to be used.
    average_risk (float): The average risk factor a message has to have to increase risk rating
    sentiment_divider (float): This divids the effect of the sentiment on risk
    max_risk (int): The max risk factor a message has to have to increase risk rating
    word_risk(int): The max risk factor a token can have before the rating is increased


    Returns:
    messages (dictionary): A dictionary of messages to be tagged, risk value, display text
    found_entities(list): A list of all special text that has been found

    Description:
    This function tags messages with relevant keywords and entities.
    """
    if chatgpt:
        label = ["PERSON", "GPE"]
    names, names_lower, locations, locations_lower = [], [], [], []
    found_entities = {label: [] for label in labels}
    if chatgpt:
        text, _ = message_to_text(messages)
        names, locations = name_location_chatgpt(text)
        names_lower, locations_lower = [name.lower() for name in names], [location.lower() for location in locations]
        found_entities[label[0]], found_entities[label[1]] = names, locations
    analyzer = SentimentIntensityAnalyzer()
    for message in messages:
        distance = 0
        message["Display_Message"] = message["Message"]
        message["risk"] = 0
        message["entities"] = []
        risk_total = 0
        message["doc"] = nlp(message["Message"])
        sentiment = analyzer.polarity_scores(message["Message"])["compound"]
        tag_list = []
        if chatgpt:
            for label in labels:
                message[label] = 0
            for entity in message["doc"].ents:
                labeled, offset, label = "", 0, ""
                if entity.text.lower() in names_lower:
                    labeled, offset = label_entity(labels[0], entity.text)
                    label = labels[0]
                elif entity.text.lower() in locations_lower:
                    labeled, offset = label_entity(labels[1], entity.text)
                    label = labels[1]
                else:
                    continue
                message["entities"].append(entity.text)
                message["Display_Message"] = (
                    message["Display_Message"][:entity.start_char + distance]
                    + labeled
                    + message["Display_Message"][entity.end_char + distance:]
                )
                distance += offset
        else:
            for label in labels:
                message[label] = 0
            for entity in message["doc"].ents:
                if entity.label_ in labels:
                    labeled, offset = label_entity(entity.label_, entity.text)
                    found_entities[entity.label_].append((entity.text))
                    message["Display_Message"] = (
                        message["Display_Message"][:entity.start_char + distance]
                        + labeled
                        + message["Display_Message"][entity.end_char + distance:]
                    )
                    distance += offset
                    message[entity.label_] += 1
                    message["entities"].append(entity.text)
        ptr = 0
        for token in message["doc"]:
            token_text = token.text
            word_regex = re.compile(
                r"(?<![a-zA-Z0-9]){}(?![a-zA-Z0-9])".format(re.escape(token_text))
            )

            if (keyword := keywords.filter(lemma=token.lemma_).first()) is not None:
                risk = keyword.risk_factor * (1 + abs(sentiment) / sentiment_divider)
                topics = keyword.topics.all()
                risk_total += risk
                if risk > word_risk:
                    message["risk"] += 1

                labeled, offset = label_keyword(token_text, keyword.keyword)

                match = word_regex.search(message["Display_Message"], ptr)
                if match:
                    start = match.start()
                    ptr = match.end() + offset
                    message["Display_Message"] = (
                        message["Display_Message"][:start]
                        + labeled
                        + message["Display_Message"][start + len(token_text):]
                    )
                    tag_list.append((keyword.keyword, risk, topics))
                    message["entities"].append(keyword.keyword)

        if risk_total > max_risk:
            message["risk"] += 1
        if risk_total / len(message["Message"].split()) > average_risk:
            message["risk"] += 1
        if message["risk"] > RISK_LEVELS:
            message["risk"] = RISK_LEVELS

        message["tags"] = tag_list
    return messages, found_entities


def get_top_n_risk_keywords(messages, n):
    """
    Arguments:
    messages (dictionary): A dictionary of tagged messages.
    n (int): The number of top keywords to retrieve.

    Returns:
    list: A list of top risky keywords along with their risk factors and counts.

    Description:
    This function retrieves the top risky keywords from tagged messages.
    """

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
    """
    Arguments:
    messages (list): A list of tagged messages.
    n (int): The number of top topics to retrieve.

    Returns:
    list: A list of top common topics along with their occurrence counts and average risk factors.

    Description:
    This function retrieves the top common topics with their average risk factors from tagged messages.
    """
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
        avg_risk_factors.append(
            [topic, topics_count[topic], risk_factors[topic] / topics_count[topic]]
        )
    return avg_risk_factors


def get_date_messages(parsed_data):
    """
    Arguments:
    parsed_data (dictionary): A dictionary of parsed message data.

    Returns:
    dict: A dictionary containing arrays for each person with timestamps and message lengths.

    Description:
    This function organizes parsed message data into arrays for each person, including timestamps and message lengths.
    """
    person_arrays = {}

    for entry in parsed_data:
        sender_name = entry.get("Sender", None)
        message_length = len(entry.get("Message", ""))

        if sender_name is not None:
            if sender_name not in person_arrays:
                person_arrays[sender_name] = {"timestamps": [], "message_lengths": []}

            person_arrays[sender_name]["timestamps"].append(entry.get("Timestamp", ""))
            person_arrays[sender_name]["message_lengths"].append(message_length)

    for person, data in person_arrays.items():
        data["timestamps"] = np.array(data["timestamps"])
        data["message_lengths"] = np.array(data["message_lengths"])

    return person_arrays


def message_to_text(list_of_messages):
    """
    Arguments:
    list_of_messages (dictionary): A dictionary of messages.

    Returns:
    tuple: A tuple containing concatenated text from messages and the original list of messages.

    Description:
    This function concatenates text from a dictionary of messages.
    """
    text = ""
    for message in list_of_messages:
        text += message.get("Message", "") + " "
    return text, list_of_messages


def create_arrays(parsed_data):
    """
    Arguments:
    parsed_data (dictionary): A dictionary of parsed data.

    Returns:
    dict: A dictionary containing arrays for each person with timestamps and message lengths.

    Description:
    This function creates arrays for each person from parsed data, including timestamps and message lengths.
    """
    person_arrays = {}

    for entry in parsed_data:
        sender_name = entry.get("Sender", None)
        message_length = len(entry.get("Message", ""))

        if sender_name is not None:
            if sender_name not in person_arrays:
                person_arrays[sender_name] = {"timestamps": [], "message_lengths": []}

            person_arrays[sender_name]["timestamps"].append(entry.get("Timestamp", ""))
            person_arrays[sender_name]["message_lengths"].append(message_length)

    # Convert the lists to NumPy arrays
    for person, data in person_arrays.items():
        data["timestamps"] = np.array(data["timestamps"])
        data["message_lengths"] = np.array(data["message_lengths"])

    return person_arrays


def get_keyword_lamma(keyword):
    """
    Arguments:
    keyword (str): The keyword to obtain lemma for.

    Returns:
    str: The lemma form of the keyword.

    Description:
    This function retrieves the lemma form of the given keyword.
    """
    doc = nlp(keyword)
    lemmas = [token.lemma_ for token in doc]
    return " ".join(lemmas)


def name_location_chatgpt(text):
    """
    Arguments:
    text (str): A whole text conversation

    Returns:
    names: TA list of names
    locations: A list of locations

    Description:
    Uses Chatgpt to find all the names and locations in the text
    """
    system_message = """I want all the names and locations form this this text, formate like this:
                    ‘names: name1,name2,name3
                    locations: location1,location2’
                    If there is neither still return like
                    'names:
                    locations:'
                    Here is the text: \n""" + text

    client = OpenAI(
            api_key=os.environ.get("CHATGPT_API_KEY"),
        )
    conversation_history = [{"role": "system", "content": system_message}, {"role": "user", "content": """I want all the names and locations form this this text, formate like this:
                    ‘names: name1,name2,name3
                    locations: location1,location2’
                    """}]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=[*conversation_history]
    )
    reply = response.choices[0].message.content
    rows = reply.split("\n")
    names, locations = rows[0].split(":")[1].split(","), rows[1].split(":")[1].split(",")
    names = [name.strip() for name in names]
    locations = [location.strip() for location in locations]
    if len(names) == 1 and names[0] == '':
        names = []
    if len(locations) == 1 and locations[0] == '':
        locations = []
    return names, locations
