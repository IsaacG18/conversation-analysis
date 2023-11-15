import numpy as np
import re
from docx import Document

def parse_chat_file(file_path, delimiters):
    # Constructing the regular expression pattern based on provided delimiters
    pattern = '^'
    for key, delim in delimiters:
        pattern += f'(.*?){delim}\s'
    pattern += '(.*)$'
    delimiters.append(["Message", ""])
    
    # Check if the file has a '.docx' extension
    if file_path.endswith('.docx'):
        doc = Document(file_path)
        lines = [paragraph.text for paragraph in doc.paragraphs]
    else:
        with open(file_path, 'r') as file:
            lines = file.readlines()

    messages = []
    for line in lines:
        # Use regular expression to extract values based on delimiters
        match = re.match(pattern, line)
        if match:
            values = match.groups()

            # Create a dictionary using keys from delimiters and corresponding values
            message_dict = {key: value for (key, _), value in zip(delimiters, values)}
            messages.append(message_dict)

    return messages

# Example usage:
file_path = 'General Chat 1.docx'  # Use the correct file path with the .docx extension
delimiters = [["Timestamp", ","], ["Sender", ":"]]
chat_messages = parse_chat_file(file_path, delimiters)

for message in chat_messages:
    print(f"Timestamp: {message['Timestamp']}, Sender: {message['Sender']}, Message: {message['Message']}")



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