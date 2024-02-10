import re
import csv
from docx import Document
from dateutil import parser
from conversation_analyst.models import DateFormat
from datetime import datetime
from dateutil import parser


def parse_timestamp(timestamp, date_formats):
    """
    Arguments:
    timestamp (str): The timestamp to parse.
    date_formats (str): The format of the timestamp.

    Returns:
    str: The parsed timestamp in the specified format.

    Description:
    This function parses a timestamp string using the provided date format.
    """
    if date_formats == "":
        return datetime.datetime.fromtimestamp(date_formats)
    else:
        return datetime.strptime(timestamp, date_formats).strftime("%Y-%m-%d %H:%M:%S")

def parse_chat_file(file_path, delimiters, date_formats="%Y-%m-%dT%H:%M:%S"):
    """
    Arguments:
    file_path (str): The path to the chat file.
    delimiters (list): A list of delimiters for splitting each line.
    date_formats (str): The format of the timestamps in the chat file. Default is ISO 8601.

    Returns:
    list: A list of dictionaries containing parsed chat messages.

    Description:
    This function parses a chat file (CSV, DOCX, TXT) and extracts messages along with their timestamps.
    """
    pattern = '^'
    for key, delim in delimiters:
        pattern += f'(.*?){delim}\\s'
    pattern += '(.*)$'
    d = list(delimiters)
    d.append(["Message", ""])
    
    messages = []
    lines = []
    try:
        if file_path.endswith('.docx'):
            try:
                doc = Document(file_path)
                lines = [paragraph.text for paragraph in doc.paragraphs]
            except Exception as e:
                raise ValueError(f"Error reading DOCX file: {e}")

        elif file_path.endswith('.csv'):
            try:
                with open(file_path, 'r') as file:
                    csv_reader = csv.reader(file)
                    next(csv_reader, None)
                    headers = [columns[0] for columns in d]
                    for row in csv_reader:
                        message_dict = {headers[i]: row[i] for i in range(len(headers))}
                        message_dict["Timestamp"] = parse_timestamp(message_dict["Timestamp"], date_formats)
                        messages.append(message_dict)
            except Exception as e:
                raise ValueError(f"Error reading CSV file: {e}")

        elif file_path.endswith('.txt'):
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
            except Exception as e:
                raise ValueError(f"Error reading TXT file: {e}")

        if file_path.endswith('.docx') or file_path.endswith('.txt'):
            for i, line in enumerate(lines):
                match = re.match(pattern, line)
                if match:
                    values = match.groups()
                    message_dict = {key: value for (key, _), value in zip(d, values)}
                    message_dict["Timestamp"] = parse_timestamp(message_dict["Timestamp"], date_formats)
                    messages.append(message_dict)
                else:
                    raise ValueError(f"Line did not match the pattern: {line} on line number {i+1}")

    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"An error occurred: {e}")
    return messages