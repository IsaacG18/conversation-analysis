import docx

# Open the Word document
doc = docx.Document('C:\\Users\\click\\Downloads\\OneDrive_2023-10-13\\sample data\\Romance Fraud Statement.docx')

chat_logs = []

# Create a flag to identify chat log sections
in_chat = False

for paragraph in doc.paragraphs:
    text = paragraph.text

    # Check if a new chat log section starts
    if text.startswith("Chat Log Excepts"):
        in_chat = True
        continue

    if in_chat and text.strip():
        # Split the text by the first comma
        parts = text.split(',', 1)
        if len(parts) == 2:
            timestamp, message = parts
            # Extract user from the message if it's in the expected format
            if ':' in message:
                user, message = message.split(':', 1)
                chat_logs.append(
                    f"Timestamp: {timestamp.strip()}, User: {user.strip()}, Message: {message.strip()}"
                )

# Print the extracted chat logs
for log in chat_logs:
    print(log)
    
    
    
    