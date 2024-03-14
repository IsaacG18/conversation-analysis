from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
import numpy as np
import re
import emoji
import os
from .chatgpt import message_openAI

nlp = []
if "NLP_VERSION" not in os.environ:
    nlp = spacy.load("en_core_web_md")
else:
    nlp = spacy.load(os.environ.get("NLP_VERSION"))
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
    start_tag = f'<span class="{classify(label)} {classify(text)} Check_181831">'
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


def tag_text(
    messages,
    keywords,
    labels,
    average_risk=0.8,
    sentiment_multiplier=2,
    max_risk=40,
    word_risk=7,
    chatgpt=False,
):
    """
    Arguments:
    messages (dictionary): A dictionary of messages to be tagged.
    keywords (list): A list of keywords objects.
    labels (list): A list of labels to be used.
    average_risk (float): The average risk factor a message has to have to increase risk rating
    sentiment_multiplier (float): This divids the effect of the sentiment on risk
    max_risk (int): The max risk factor a message has to have to increase risk rating
    word_risk(int): The max risk factor a token can have before the rating is increased


    Returns:
    messages (dictionary): A dictionary of messages to be tagged, risk value, display text
    found_entities(list): A list of all special text that has been found

    Description:
    This function tags messages with relevant keywords and entities.
    """
    lemma_dict = {}
    for keyword in keywords:
        lemma_dict[keyword.lemma] = {"topics": keyword.topics.all(), "keyword": keyword.keyword, "risk_factor": keyword.risk_factor}
    if chatgpt:
        labels = ["PERSON", "GPE"]
    names, locations = [], []
    found_entities = {label: [] for label in labels}
    if chatgpt:
        text, _ = message_to_text(messages)
        names, locations = name_location_chatgpt(text)
        result = []
        for item in locations:
            if item not in names:
                result.append(item)
        locations = result
        found_entities[labels[0]], found_entities[labels[1]] = names, locations
    analyzer = SentimentIntensityAnalyzer()
    for message in messages:
        distance, risk_total, tag_list = 0, 0, []
        (
            message["Display_Message"],
            message["risk"],
            message["entities"],
            message["doc"],
        ) = (message["Message"], 0, [], nlp(message["Message"]))
        sentiment = analyzer.polarity_scores(message["Message"])["compound"]

        for label in labels:
            message[label] = 0

        if chatgpt:
            chatgpt_find(message, labels[0], names)
            chatgpt_find(message, labels[1], locations)
        else:
            for entity in message["doc"].ents:
                if entity.label_ in labels and emoji.emoji_count(entity.text) == 0:
                    labeled, offset = label_entity(entity.label_, entity.text)
                    found_entities[entity.label_].append((entity.text))
                    update_display(entity.start_char + distance, entity.end_char + distance, message, labeled)
                    distance += offset
                    message[entity.label_] += 1
                    message["entities"].append(entity.text)
        ptr = 0
        for token in message["doc"]:
            token_text = token.text
            word_regex = re.compile(
                r"(?<![a-zA-Z0-9]){}(?![a-zA-Z0-9])".format(re.escape(token_text))
            )
            keyword = lemma_dict.get(token.lemma_)
            if (keyword is not None):
                risk = keyword["risk_factor"] * (1 + abs(sentiment) / sentiment_multiplier)
                topics = keyword["topics"]
                risk_total += risk
                if risk > word_risk:
                    message["risk"] += 1

                labeled, offset = label_keyword(token_text, keyword["keyword"])
                match = word_regex.search(message["Display_Message"], ptr)
                if match:
                    if (
                        message["Display_Message"][
                            match.start() - 7:match.start() - 1
                        ]
                        == "PERSON"
                        or message["Display_Message"][
                            match.start() - 4:match.start() - 1
                        ]
                        == "GPE"
                    ) and message["Display_Message"][
                        match.end() + 1:match.end() + 13
                    ] == "Check_181831":
                        ptr = match.end() + offset
                        update_display(match.end(), match.end(), message, " risk ")
                        tag_list.append((keyword["keyword"], keyword["risk_factor"], topics))
                        message["entities"].append(keyword["keyword"])
                    else:
                        start = match.start()
                        ptr = match.end() + offset
                        update_display(start, start + len(token_text), message, labeled)
                        tag_list.append((keyword["keyword"], keyword["risk_factor"], topics))
                        message["entities"].append(keyword["keyword"])
        if risk_total > max_risk:
            message["risk"] += 1
        if risk_total / len(message["Message"].split()) > average_risk:
            message["risk"] += 1
        if message["risk"] > RISK_LEVELS:
            message["risk"] = RISK_LEVELS
        message["tags"] = tag_list

    return messages, found_entities


def update_display(start, end, message, text):
    """
    Arguments:
    start (int): The start index of the split in the message
    end (int): The end index of the split in the message
    message (dict): This is a dictionary that contraits a key Display_Message
    text (text): A string

    Description:
    Adds the text in between the start and end point in message display message
    """
    message["Display_Message"] = message["Display_Message"][:start] + text + message["Display_Message"][end:]


def get_top_n_risk_keywords(messages, n=-1):
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
    sorted_tokens = []
    for message in messages:
        for keyword, risk, topics in message["tags"]:
            if risk != 0:
                if keyword not in token_risk:
                    token_risk[keyword] = risk
                if keyword in token_count:
                    token_count[keyword] += 1
                else:
                    token_count[keyword] = 1
    sorted_tokens = sorted(token_risk, key=lambda x: token_risk[x], reverse=True)
    if n != -1:
        sorted_tokens = sorted_tokens[:n]
    result = [(token, token_risk[token], token_count[token]) for token in sorted_tokens]
    return result


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
    system_message = (
        """I want all the person names and locations form this this text, formate like this:
                    'persons: name1,name2,name3
                    locations: location1,location2'
                    If there is a colon in the middle of location or person, they should be treated as a seperate person or location.
                    If there is neither still return like
                    'persons:
                    locations:'
                    Here is the text: \n"""
        + text
    )
    conversation_history = [
        {"role": "system", "content": system_message},
        {
            "role": "user",
            "content": """I want all person names and locations form this this text, formate like this:
                    persons: name1,name2,name3
                    locations: location1,location2
                    """,
        },
    ]
    reply, conversation_history = message_openAI(conversation_history)
    if conversation_history is None:
        return [], []
    rows = reply.split("\n")
    try:
        names, locations = (
            rows[0].split(":")[1].split(","),
            rows[1].split(":")[1].split(","),
        )
        names = [name.strip() for name in names]
        locations = [location.strip() for location in locations]
        if len(names) == 1 and names[0] == "":
            names = []
        if len(locations) == 1 and locations[0] == "":
            locations = []
    except IndexError:
        names = []
        locations = []
    return names, locations


def chatgpt_find(message, chat_type, chat_list):
    """
    Arguments:
    message (dict): Contains the data, and extra data about the message

    Description:
    Replaces the display text to inluded the HTML tags
    """
    for item in chat_list:
        label, offset = label_entity(chat_type, item)
        if item in message["Display_Message"]:
            message["entities"].append(item)
            message["Display_Message"] = message["Display_Message"].replace(item, label)
            message[chat_type] += 1
