import os
from os.path import isfile, join

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tp3.settings")
import django

django.setup()

from conversation_analyst.scripts.data_ingestion import ingestion
from conversation_analyst.scripts.object_creators import add_delim, add_date


def populate_dates():
    date_formats = [
        {
            "name": "ISO 8601",
            "example": "2022-01-24T12:34:56",
            "format": "%Y-%m-%dT%H:%M:%S",
            "default": True,
        },
        {
            "name": "Unix Timestamp",
            "example": "1643057699",
            "format": r"^\d{10}(?:\.\d+)?$",
            "default": False,
        },
        {
            "name": "Common Log Format",
            "example": "01/Feb/2024:12:34:56 +0000",
            "format": "%d/%b/%Y:%H:%M:%S %z",
            "default": False,
        },
        {
            "name": "ISO 8601 Without Seconds",
            "example": "2022-03-05 17:30",
            "format": "%Y-%m-%d %H:%M",
            "default": False,
        },
    ]

    for date_format_data in date_formats:
        add_date(
            date_format_data["name"],
            date_format_data["example"],
            date_format_data["format"],
            date_format_data["default"],
        )


def populate_delims():
    delimiters = [
        {"name": "Timestamp", "order": "1", "value": ",", "is_default": "True"},
        {"name": "Sender", "order": "2", "value": ":", "is_default": "True"},
    ]

    for delim in delimiters:
        add_delim(delim["name"], delim["order"], delim["value"], delim["is_default"])


if __name__ == "__main__":
    print("Starting population script...")
    populate_dates()
    populate_delims()
    print("Finished")
