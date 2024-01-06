import re
import csv
from docx import Document

def parse_chat_file(file_path, delimiters):
    pattern = '^'
    for key, delim in delimiters:
        pattern += f'(.*?){delim}\s'
    pattern += '(.*)$'
    d = list (delimiters)
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
                    messages.append(message_dict)
                else:
                    raise ValueError(f"Line did not match the pattern: {line} on line number {i+1}")

    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"An error occurred: {e}")
    return messages