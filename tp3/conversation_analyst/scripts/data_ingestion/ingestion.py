import re
import csv
from docx import Document
from dateutil import parser
from conversation_analyst.models import DateFormat
from datetime import datetime
from dateutil import parser

def get_date_formats():
    formats = DateFormat.objects.all()
    print([(fmt.name, re.compile(fmt.regex)) for fmt in formats])
    return [(fmt.name, re.compile(fmt.regex)) for fmt in formats]

def parse_specific_format(timestamp, format_name):
    # Add custom parsing logic here:
    if format_name == "ISO 8601":
        return parser.parse(timestamp)

    elif format_name == "Unix Timestamp":
        return datetime.utcfromtimestamp(int(timestamp))

    elif format_name == "Common Log Format":
        match = re.search(r'\[([^:]+):(\d+:){2}\d+ ([^\]]+)\]', timestamp)
        if match:
            timestamp_str = match.group(1) + ' ' + match.group(3)
            datetime_obj = datetime.strptime(timestamp_str, '%d/%b/%Y %H:%M:%S %z')
            return datetime_obj
        
    elif format_name == "ISO 8601 Without Seconds":
        return datetime.strptime(timestamp, '%Y-%m-%d %H:%M')

    else:
        raise ValueError(f"Unrecognized format name: {format_name}")

    return datetime_obj.isoformat()

def parse_timestamp(timestamp, date_formats):
    for name, regex in date_formats:
        if regex.match(timestamp):
            return parse_specific_format(timestamp, name).isoformat()
    raise ValueError(f"Unrecognized timestamp format: {timestamp}")

def parse_chat_file(file_path, delimiters):
    pattern = '^'
    for key, delim in delimiters:
        pattern += f'(.*?){delim}\\s'
    pattern += '(.*)$'
    d = list(delimiters)
    d.append(["Message", ""])
    
    messages = []
    lines = []

    date_formats = get_date_formats()

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