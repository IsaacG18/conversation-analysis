import re
import csv
from docx import Document
from dateutil import parser
from conversation_analyst.models import DateFormat
from datetime import datetime
from dateutil import parser


def parse_timestamp(timestamp, date_formats):
    if date_formats == "":
        return datetime.datetime.fromtimestamp(date_formats)
    else:
        return datetime.strptime(timestamp, date_formats).strftime("%Y-%m-%d %H:%M:%S")

def parse_chat_file(file_path, delimiters, date_formats="%Y-%m-%dT%H:%M:%S"):
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