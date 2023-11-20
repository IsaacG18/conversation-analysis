import re
from docx import Document

def parse_chat_file(file_path, delimiters):
    pattern = '^'
    for key, delim in delimiters:
        pattern += f'(.*?){delim}\s'
    pattern += '(.*)$'
    delimiters.append(["Message", ""])

    try:
        if file_path.endswith('.docx'):
            doc = Document(file_path)
            lines = [paragraph.text for paragraph in doc.paragraphs]
        else:
            with open(file_path, 'r') as file:
                lines = file.readlines()

        messages = []
        for line in lines:
            match = re.match(pattern, line)
            if match:
                values = match.groups()

                message_dict = {key: value for (key, _), value in zip(delimiters, values)}
                messages.append(message_dict)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return messages