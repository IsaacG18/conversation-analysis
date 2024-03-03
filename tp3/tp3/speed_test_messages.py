import os
from os.path import isfile, join

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tp3.settings")
import django

django.setup()

from conversation_analyst.scripts.data_ingestion.file_process import process_file
from conversation_analyst.tests import add_message, add_custom_threshold
from django.utils import timezone
from conversation_analyst.models import RiskWord, CustomThresholds, File, KeywordSuite

def add_chat_messages(messages):
    keywords_array = []
    messages_array = []
    file = File.objects.create(
        file="uploads/sample_file1.txt",
        title="Sample File 1",
        format="txt",
        slug="sample-file-1-" + timezone.now().strftime("%Y%m%d%H%M%S"),
    )

    for message in messages:
        messages_array.append(add_message(file, timezone.now(), "Sender", message))


    suite_obj = KeywordSuite.objects.create(name="suite")
    

    keywords_array.append(RiskWord.objects.create(suite=suite_obj, keyword="apple", risk_factor=10))
    keywords_array.append(RiskWord.objects.create(suite=suite_obj, keyword="day", risk_factor=10))
    keywords_array.append(RiskWord.objects.create(suite=suite_obj, keyword="you", risk_factor=10))
    keywords_array.append(RiskWord.objects.create(suite=suite_obj, keyword="beautiful", risk_factor=10))

    keywords = RiskWord.objects.filter(suite=suite_obj)
    threshold = add_custom_threshold(average_risk=0.8, sentiment_multiplier=2, max_risk=40, word_risk=7)

    suite_obj.delete()
 
    process_file(file, keywords, messages_array, threshold)

    #suite_obj.delete()
    file.delete()
    
    threshold.delete()

    for keyword in keywords_array:
        keyword.delete()
    for message in messages_array:
        message.delete()



if __name__ == "__main__":

    messages_1 = []

    with open("messages.txt", "r") as file:
        lines = [line.strip() for line in file.readlines()]
        for line in lines: messages_1.append(line)
    
    add_chat_messages(messages_1)