import os
from os.path import isfile, join

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tp3.settings')
import django

django.setup()

from conversation_analyst.scripts.data_ingestion import ingestion
from conversation_analyst.scripts.nlp.nlp import *
from conversation_analyst.scripts.object_creators import *
from conversation_analyst.views import generate_analysis_objects


def populate_dates():
    date_formats = [
        {"name": "ISO 8601", "example": "2022-01-24T12:34:56", "regex": r'^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(\.\d+)?(Z|[+-]\d{2}:\d{2})?$'},
        {"name": "Unix Timestamp", "example": "1643057699", "regex": r'^(\d+)$'},
        {"name": "Common Log Format", "example": '127.0.0.1 - - [24/Jan/2022:12:34:56 +0300] "GET /example" 200 123', "regex": r'^(\S+) (\S+) (\S+) \[([^:]+):(\d+:){2}\d+ ([^\]]+)\] "(\S+ \S+ \S+)" (\d{3}) (\d+|-)$'}
    ]

    for date_format_data in date_formats:
        add_date(date_format_data["name"], date_format_data["example"], date_format_data["regex"])

if __name__ == '__main__':
    print('Starting population script...')
    populate_dates()
    print('Finished')