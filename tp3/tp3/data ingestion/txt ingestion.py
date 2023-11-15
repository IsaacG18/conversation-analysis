import re
import spacy

def txt_ingest_to_spacy(file_path):
    # Load the SpaCy English model
    nlp = spacy.load("en_core_web_sm")

    # Define regular expression patterns to match different timestamp and message formats
    patterns = [
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}), ([^:]+): (.+)',  # Pattern 1: 'YYYY-MM-DD HH:MM, User: Message'
        r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}), ([^:]+): (.+)',  # Pattern 2: 'YYYY-MM-DDTHH:MM:SS, User: Message' or 'YYYY-MM-DD HH:MM:SS, User: Message'
    ]

    chat_logs = []

    try:
        # Open the file and read the chat logs
        with open(file_path, 'r', encoding='utf-8') as file:
            print(f"File '{file_path}' opened successfully.")
            lines = file.readlines()

        for line in lines:
            matched = False
            for pattern in patterns:
                message_match = re.search(pattern, line.strip())
                if message_match:
                    timestamp = message_match.group(1)
                    user = message_match.group(2)
                    message = message_match.group(3)
                    chat_logs.append((timestamp, user, message))
                    matched = True
                    break
            if not matched:
                print(f"No match found for line: {line.strip()}")

        # Print the extracted chat logs
        for log in chat_logs:
            print(f"Timestamp: {log[0]}, User: {log[1]}, Message: {log[2]}")
            print(f"Message: {log[2]}")


        # Process messages with SpaCy
        processed_chat_logs = []

        for log in chat_logs:
            timestamp, user, message = log

            # Use SpaCy to process the message
            doc = nlp(message)

            # Access SpaCy's linguistic annotations
            tokens = [token.text for token in doc]
            pos_tags = [token.pos_ for token in doc]

            # Append processed data to the list
            processed_chat_logs.append({
                "timestamp": timestamp,
                "user": user,
                "message": message,
                "tokens": tokens,
                "pos_tags": pos_tags
            })


    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")