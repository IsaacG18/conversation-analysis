import re

# Define regular expression patterns to match different timestamp and message formats
patterns = [
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}), ([^:]+): (.+)', # Pattern 1: 'YYYY-MM-DD HH:MM, User: Message'
    r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}), ([^:]+): (.+)', # Pattern 2: 'YYYY-MM-DDTHH:MM:SS, User: Message' or 'YYYY-MM-DD HH:MM:SS, User: Message'
]

chat_logs = []

# Replace with your actual file path
file_path = 'C:\\Users\\click\\Desktop\\chat_logs\\txt\\Romance Fraud Sample 3\\romanceFraudJacobEmily.txt'

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
        #print(f"Timestamp: {log[0]}, User: {log[1]}, Message: {log[2]}")
        print(f"Message: {log[2]}")

except FileNotFoundError:
    print(f"File not found: {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
