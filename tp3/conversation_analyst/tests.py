from django.test import TestCase, Client
from django.urls import reverse
import unittest
from .models import (
    Delimiter,
    File,
    Analysis,
    Person,
    Location,
    VisFile,
    DateFormat,
    KeywordSuite,
    RiskWord,
    ChatGPTConvo,
    ChatGPTMessage,
    ChatGPTFilter,
    ChatGPTConvoFilter,
    CustomThresholds,
    RiskWordResult,
    Topic,
)
from .scripts.nlp.nlp import (
    classify,
    get_top_n_risk_keywords,
    label_entity,
    label_keyword,
    message_to_text,
    get_date_messages,
    get_keyword_lamma,
    tag_text,
    name_location_chatgpt,
    update_display,
)
from django.utils import timezone
from django.template.defaultfilters import slugify
from .scripts.object_creators import (
    Message,
    add_message,
    update_message,
    add_analysis,
    add_person,
    add_location,
    add_vis,
    add_date,
    add_delim,
    add_chat_message,
    add_chat_filter,
    add_custom_threshold,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from .scripts.data_ingestion.plotter import plots
from unittest.mock import patch, MagicMock
from .scripts.data_ingestion.file_process import (
    parse_file,
    process_file,
    generate_analysis_objects,
)
from conversation_analyst.scripts.data_ingestion.ingestion import (
    parse_chat_file,
    parse_timestamp,
)
import os
import numpy as np
import spacy
import tempfile
import csv
from docx import Document
from datetime import datetime

nlp = []
if "NLP_VERSION" not in os.environ:
    nlp = spacy.load("en_core_web_md")
else:
    nlp = spacy.load(os.environ.get("NLP_VERSION"))


# Create your tests here.
class DelimiterTestCase(TestCase):
    def setUp(self):
        Delimiter.objects.create(name="Comma", value=",", order=1, is_default=True)
        Delimiter.objects.create(name="Semicolon", value=";", order=2, is_default=False)

    def test_delimiter_creation(self):
        """Test the delimiter instances are correctly created."""
        comma = Delimiter.objects.get(name="Comma")
        semicolon = Delimiter.objects.get(name="Semicolon")
        self.assertEqual(comma.get_value(), ",")
        self.assertEqual(semicolon.get_value(), ";")

    def test_delimiter_order(self):
        """Test the order attribute works correctly."""
        comma = Delimiter.objects.get(name="Comma")
        semicolon = Delimiter.objects.get(name="Semicolon")
        self.assertEqual(comma.get_order(), 1)
        self.assertEqual(semicolon.get_order(), 2)

    def test_delimiter_default(self):
        """Test the is_default attribute works correctly."""
        comma = Delimiter.objects.get(name="Comma")
        semicolon = Delimiter.objects.get(name="Semicolon")
        self.assertTrue(comma.is_default)
        self.assertFalse(semicolon.is_default)

    def test_delimiter_str(self):
        """Test the __str__ method returns the name."""
        comma = Delimiter.objects.get(name="Comma")
        self.assertEqual(str(comma), "Comma")

    def test_delimiter_large_order(self):
        """Test handling of large order values."""
        large_order_value = 2**31
        delimiter = Delimiter.objects.create(
            name="Pipe", value="|", order=large_order_value, is_default=False
        )
        self.assertEqual(delimiter.order, large_order_value)

    def test_delimiter_str_special_characters(self):
        """Test the __str__ method with special characters."""
        name_with_special_chars = "Newline\nCarriage Return\r"
        delimiter = Delimiter.objects.create(
            name=name_with_special_chars, value="\n", order=5, is_default=False
        )
        self.assertEqual(str(delimiter), name_with_special_chars)


class SearchFeatureTests(TestCase):
    def setUp(self):
        File.objects.create(
            file="uploads/sample_file1.txt",
            title="Sample File 1",
            format="txt",
            slug="sample-file-1-" + timezone.now().strftime("%Y%m%d%H%M%S"),
        )
        File.objects.create(
            file="uploads/sample_file2.txt",
            title="Sample Search File",
            format="txt",
            slug="sample-search-file-" + timezone.now().strftime("%Y%m%d%H%M%S"),
        )

    def test_search_feature(self):
        response = self.client.get(reverse("homepage"), {"query": "Search"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sample Search File")
        self.assertNotContains(response, "Sample File 1")

    def test_search_with_special_characters(self):
        response = self.client.get(reverse("homepage"), {"query": "Sample & File"})
        self.assertEqual(response.status_code, 200)

    def test_search_case_insensitivity(self):
        response = self.client.get(reverse("homepage"), {"query": "sample search file"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sample Search File")

    def test_empty_query(self):
        response = self.client.get(reverse("homepage"), {"query": ""})
        self.assertEqual(response.status_code, 200)

    def test_very_long_query(self):
        long_query = "a" * 1000
        response = self.client.get(reverse("homepage"), {"query": long_query})
        self.assertEqual(response.status_code, 200)

    def test_non_existing_query(self):
        response = self.client.get(reverse("homepage"), {"query": "NonExisting"})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Sample File 1")
        self.assertNotContains(response, "Sample Search File")

    def test_sql_injection_protection(self):
        response = self.client.get(
            reverse("homepage"), {"query": "'; DROP TABLE files; --"}
        )
        self.assertEqual(response.status_code, 200)


class ObjectCreatorTests(TestCase):
    def setUp(self):
        self.file = File.objects.create(
            file="test_file.txt", title="Test File", format="txt"
        )
        self.analysis = Analysis.objects.create(file=self.file)
        self.convo = ChatGPTConvo.objects.create(file=self.file, title="Test Convo")

    def test_add_message(self):
        message = add_message(self.file, timezone.now(), "Sender", "Test message")
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.content, "Test message")
        self.assertEqual(message.sender, "Sender")

    def test_update_message(self):
        message = Message.objects.create(
            file=self.file,
            timestamp=timezone.now(),
            sender="Sender",
            content="Test message",
        )
        updated_message = update_message(
            message.id, "Updated message", ["entity1", "entity2"], risk_rating=3
        )
        self.assertEqual(updated_message.display_content, "Updated message")
        self.assertEqual(updated_message.tags, "entity1,entity2")
        self.assertEqual(updated_message.risk_rating, 3)

    def test_add_analysis(self):
        new_analysis = add_analysis(self.file)
        self.assertEqual(Analysis.objects.count(), 1)
        self.assertEqual(new_analysis.file, self.file)

    def test_add_person(self):
        person = add_person(self.analysis, "John Doe")
        self.assertEqual(Person.objects.count(), 1)
        self.assertEqual(person.name, "John Doe")

    def test_add_location(self):
        location = add_location(self.analysis, "New York")
        self.assertEqual(Location.objects.count(), 1)
        self.assertEqual(location.name, "New York")

    def test_add_vis(self):
        vis = add_vis(self.analysis, "visualizations/test.png")
        self.assertEqual(VisFile.objects.count(), 1)
        self.assertEqual(vis.file_path, "visualizations/test.png")

    def test_add_date(self):
        date_format = add_date(
            "ISO 8601", "2022-02-10T14:30:00", "%Y-%m-%dT%H:%M:%S", True
        )
        self.assertEqual(DateFormat.objects.count(), 1)
        self.assertEqual(date_format.name, "ISO 8601")
        self.assertEqual(date_format.format, "%Y-%m-%dT%H:%M:%S")
        self.assertTrue(date_format.is_default)

    def test_add_delim(self):
        delimiter = add_delim("Comma", 1, ",", True)
        self.assertEqual(Delimiter.objects.count(), 1)
        self.assertEqual(delimiter.name, "Comma")
        self.assertEqual(delimiter.value, ",")
        self.assertTrue(delimiter.is_default)

    def test_add_chat_message(self):
        chat_message = add_chat_message("Incoming", "Hello!", self.convo)
        self.assertEqual(ChatGPTMessage.objects.count(), 1)
        self.assertEqual(chat_message.content, "Hello!")

    def test_add_chat_filter(self):
        chat_filter, convo_filter = add_chat_filter("spam", "Filter", self.convo)
        self.assertEqual(ChatGPTFilter.objects.count(), 1)
        self.assertEqual(chat_filter.content, "spam")
        self.assertEqual(ChatGPTConvoFilter.objects.count(), 1)
        self.assertEqual(convo_filter.filter.content, "spam")

    def test_add_custom_threshold(self):
        ct = add_custom_threshold(
            average_risk=0.8, sentiment_multiplier=2, max_risk=40, word_risk=7
        )
        self.assertEqual(CustomThresholds.objects.count(), 1)
        self.assertEqual(ct.average_risk, 0.8)
        self.assertEqual(ct.sentiment_multiplier, 2)
        self.assertEqual(ct.max_risk, 40)
        self.assertEqual(ct.word_risk, 7)

    # def test_update_non_existing_message(self):
    #     with self.assertRaises(Message.DoesNotExist):
    #         update_message(999, "Non-existing message", ["entity3", "entity4"], risk_rating=5)

    # def test_add_person_with_long_name(self):
    #     long_name = "John" * 50
    #     person = add_person(self.analysis, long_name)
    #     self.assertTrue(len(person.name) <= 50)

    # def test_add_large_number_of_messages(self):
    #     initial_count = Message.objects.count()
    #     for _ in range(10000):
    #         add_message(self.file, timezone.now(), "Mass Sender", "Mass message")
    #     expected_count = initial_count + 10000
    #     self.assertEqual(Message.objects.count(), expected_count)


class RenameTests(TestCase):
    def setUp(self):
        self.file1 = File.objects.create(
            file="uploads/sample_file1.txt",
            title="Sample File 1",
            format="txt",
            slug="sample-file-1-" + timezone.now().strftime("%Y%m%d%H%M%S"),
        )

    def test_rename(self):
        new_title = "Renamed Sample File"
        new_title_with_extension = f"{new_title}.txt"
        response = self.client.post(
            reverse("rename_file"),
            {"fileName": new_title, "fileId": self.file1.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        updated_file = File.objects.get(id=self.file1.id)
        updated_file.refresh_from_db()
        self.assertEqual(updated_file.title, new_title_with_extension)
        self.assertJSONEqual(
            str(response.content, encoding="utf8"),
            {
                "message": f"file name of file {self.file1.id} is updated to {new_title_with_extension}",
                "fileName": new_title_with_extension,
            },
        )


class TestTagText(TestCase):
    def setUp(self):
        self.messages = [
            {
                "Message": "Apple is a tech company and it's headquartered in Cupertino.",
                "risk": 0,
            },
            {"Message": "I love bananas and apples.", "risk": 0},
        ]
        suite_obj = KeywordSuite.objects.create(name="suite_name")
        suite_obj.save()
        risk_obj = RiskWord.objects.create(
            suite=suite_obj, keyword="apple", risk_factor=10
        )
        risk_obj.save()
        self.keywords = RiskWord.objects.filter(suite=suite_obj)
        self.labels = ["ORG", "GPE"]

    def test_tag_text_entity_labeling(self):
        labeled_messages, found_entities = tag_text(
            self.messages, self.keywords, self.labels
        )
        self.assertEqual(labeled_messages[0]["ORG"], 1)
        self.assertEqual(labeled_messages[0]["GPE"], 1)
        self.assertEqual(found_entities["ORG"], ["Apple"])
        self.assertEqual(found_entities["GPE"], ["Cupertino"])

    def test_tag_text_keyword_labeling(self):
        labeled_messages, _ = tag_text(self.messages, self.keywords, self.labels)
        self.assertEqual(labeled_messages[0]["risk"], 0)
        self.assertEqual(labeled_messages[1]["risk"], 2)

    def test_tag_text_edge_cases(self):
        empty_messages = []
        labeled_empty_messages, _ = tag_text(empty_messages, self.keywords, self.labels)
        self.assertEqual(labeled_empty_messages, [])

    def test_tag_text(self):
        emoji_message = [{"Message": "😊", "risk": 0}]
        labeled_empty_messages, found_entities = tag_text(emoji_message, self.keywords, ["PERSON"])
        self.assertEqual(len(found_entities["PERSON"]), 0)


class TestNLP(TestCase):
    def setUp(self):
        self.messages = [
            {
                "tags": [
                    ("risk1", 0.5, ["topic1", "topic2"]),
                    ("risk2", 0.3, ["topic1"]),
                ],
                "Message": "Hello",
                "Sender": "Alice",
                "Timestamp": "2024-02-10 08:00:00",
            },
            {
                "tags": [
                    ("risk3", 0.7, ["topic2", "topic3"]),
                    ("risk4", 0.2, ["topic3"]),
                ],
                "Message": "Hi there",
                "Sender": "Bob",
                "Timestamp": "2024-02-10 08:05:00",
            },
        ]

    def test_get_top_n_risk_keywords(self):
        top_keywords = get_top_n_risk_keywords(self.messages, 2)
        expected_result = [("risk3", 0.7, 1), ("risk1", 0.5, 1)]
        self.assertEqual(top_keywords, expected_result)

    def test_get_top_n_risk_keywords_not_number(self):
        top_keywords = get_top_n_risk_keywords(self.messages)
        expected_result = [('risk3', 0.7, 1), ('risk1', 0.5, 1), ('risk2', 0.3, 1), ('risk4', 0.2, 1)]
        self.assertEqual(top_keywords, expected_result)

    def test_get_date_messages(self):
        parsed_data = [
            {"Sender": "Alice", "Message": "Hello", "Timestamp": "2024-02-10 08:00:00"},
            {
                "Sender": "Bob",
                "Message": "Hi there",
                "Timestamp": "2024-02-10 08:05:00",
            },
            {
                "Sender": "Alice",
                "Message": "How are you?",
                "Timestamp": "2024-02-10 08:10:00",
            },
        ]
        date_messages = get_date_messages(parsed_data)

        self.assertIsInstance(date_messages["Alice"]["timestamps"], np.ndarray)
        self.assertEqual(len(date_messages["Alice"]["timestamps"]), 2)
        self.assertEqual(date_messages["Alice"]["timestamps"][0], "2024-02-10 08:00:00")
        self.assertEqual(date_messages["Alice"]["timestamps"][1], "2024-02-10 08:10:00")

        self.assertIsInstance(date_messages["Alice"]["message_lengths"], np.ndarray)
        self.assertEqual(len(date_messages["Alice"]["message_lengths"]), 2)
        self.assertEqual(date_messages["Alice"]["message_lengths"][0], 5)
        self.assertEqual(date_messages["Alice"]["message_lengths"][1], 12)

        self.assertIsInstance(date_messages["Bob"]["timestamps"], np.ndarray)
        self.assertEqual(len(date_messages["Bob"]["timestamps"]), 1)
        self.assertEqual(date_messages["Bob"]["timestamps"][0], "2024-02-10 08:05:00")

        self.assertIsInstance(date_messages["Bob"]["message_lengths"], np.ndarray)
        self.assertEqual(len(date_messages["Bob"]["message_lengths"]), 1)
        self.assertEqual(date_messages["Bob"]["message_lengths"][0], 8)

    def test_classify(self):
        self.assertEqual(classify("Some Text"), "Some_Text")
        self.assertEqual(classify("Another Text"), "Another_Text")
        self.assertEqual(classify("Yet Another Text"), "Yet_Another_Text")

    def test_label_entity(self):
        for entity in nlp("OpenAI").ents:
            labeled_text, offset = label_entity(entity.label_, entity.text)
            self.assertEqual(labeled_text, '<span class="ORG OpenAI">OpenAI</span>')
            self.assertEqual(offset, 28)

    def test_label_keyword(self):
        keyword = "risk"
        root = "ROOT"
        labeled_text, offset = label_keyword(keyword, root)
        self.assertEqual(labeled_text, '<span class="ROOT risk">risk</span>')
        self.assertEqual(offset, 31)

    def test_message_to_text(self):
        messages = [
            {"Message": "Hello", "Sender": "Alice"},
            {"Message": "Hi there", "Sender": "Bob"},
            {"Message": "How are you?", "Sender": "Alice"},
        ]
        expected_text = "Hello Hi there How are you? "
        text, _ = message_to_text(messages)
        self.assertEqual(text, expected_text)

    def test_get_keyword_lamma(self):
        keyword = "running"
        expected_lemma = "run"
        lemma = get_keyword_lamma(keyword)
        self.assertEqual(lemma, expected_lemma)

    def test_name_location_chatgpt_empty(self):
        names, locations = name_location_chatgpt("HERE")
        self.assertEqual(0, len(names))
        self.assertEqual(0, len(locations))

    def test_name_location_chatgpt(self):
        names, locations = name_location_chatgpt(
            "Hello, I am Isaac, and I am from Dundee"
        )
        self.assertEqual(1, len(names))
        self.assertEqual(1, len(locations))
        self.assertEqual("Isaac", names[0])
        self.assertEqual("Dundee", locations[0])

    def test_label_entity_with_invalid_entity(self):
        # Test with invalid entity that does not have label_ or text
        with self.assertRaises(AttributeError):
            label_entity(None, None)

    def test_message_to_text_with_empty_messages(self):
        # Test with empty messages list
        text, _ = message_to_text([])
        self.assertEqual(text, "")

    def test_name_location_chatgpt_with_non_string_input(self):
        # Test with non-string input
        with self.assertRaises(TypeError):
            name_location_chatgpt(None)

    def test_name_location_chatgpt_with_long_string(self):
        # Test with a very long string to test the limits of the NLP model
        long_string = (
            "Hello, I am Isaac, "
            + "and I love visiting cities, " * 1000
            + "and I am from Dundee"
        )
        names, locations = name_location_chatgpt(long_string)
        self.assertEqual(1, len(names))
        self.assertEqual(1, len(locations))
        self.assertEqual("Isaac", names[0])
        self.assertEqual("Dundee", locations[0])

    def test_message_to_text_with_large_number_of_messages(self):
        # Test with a large number of messages
        large_messages = [{"Message": "Hello", "Sender": "Alice"}] * 10000
        text, _ = message_to_text(large_messages)
        self.assertTrue(len(text) > 0)

    def test_update_message_normal(self):
        message = {}
        message["Display_Message"] = "Hello!"
        update_display(5, 5, message, "World")
        self.assertEqual("HelloWorld!", message["Display_Message"])

    def test_update_message_extreme_one(self):
        message = {}
        message["Display_Message"] = "Hello i am ,how are you"
        update_display(11, 10, message, "David")
        self.assertEqual("Hello i am David ,how are you", message["Display_Message"])

    def test_update_message_extreme_two(self):
        message = {}
        message["Display_Message"] = ""
        update_display(0, 0, message, "")
        self.assertEqual(message["Display_Message"], "")


class ChatGPTFeatureTestCase(TestCase):
    def setUp(self):
        # Create a File instance as required
        test_file = File.objects.create(file="path/to/file", title="Test File")
        # Explicitly set the title for the ChatGPTConvo instance
        self.test_convo = ChatGPTConvo.objects.create(
            title="Test Conversation", file=test_file, date=timezone.now()
        )

    def test_chatgpt_message_creation(self):
        """Test adding messages to a ChatGPTConvo."""
        ChatGPTMessage.objects.create(
            typeOfMessage="Question",
            content="This is a test question?",
            convo=self.test_convo,
        )
        ChatGPTMessage.objects.create(
            typeOfMessage="Response",
            content="This is a test answer.",
            convo=self.test_convo,
        )

        messages = ChatGPTMessage.objects.filter(convo=self.test_convo)
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].content, "This is a test question?")
        self.assertEqual(messages[1].typeOfMessage, "Response")


class SettingTestCase(TestCase):
    def setUp(self):
        self.suite = KeywordSuite.objects.create(name="Init Suite")

    def test_create_suite(self):
        self.client.post(
            reverse("create_suite"),
            {"name": "New Suite"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertTrue(KeywordSuite.objects.filter(name="New Suite").exists())

    def test_delete_suite(self):
        suite_to_delete = KeywordSuite.objects.create(name="Delete")
        self.client.get(
            reverse("delete_suite"),
            {"suiteId": suite_to_delete.id},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertFalse(KeywordSuite.objects.filter(name="Delete").exists())

    def test_create_risk_word(self):
        self.client.post(
            reverse("create_keyword"),
            {"keyword": "New RiskWord", "suite": self.suite.name, "risk": 5},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertTrue(RiskWord.objects.filter(keyword="New RiskWord").exists())

    def test_update_risk_factor(self):
        risk_word_to_update = RiskWord.objects.create(
            suite=self.suite, keyword="RiskWordToUpdate", risk_factor=5
        )
        new_risk_factor = 7
        self.client.post(
            reverse("risk_update"),
            {"keyword": risk_word_to_update.id, "risk": new_risk_factor},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        risk_word_to_update.refresh_from_db()
        self.assertEqual(risk_word_to_update.risk_factor, new_risk_factor)


class InputValidationTestCase(TestCase):
    def setUp(self):
        DateFormat.objects.create(
            name="some_valid_timestamp",
            example="2023-01-01T00:00:00",
            format="%Y-%m-%dT%H:%M:%S",
            is_default=True,
        )

    def test_invalid_form_data(self):
        uploaded_file = SimpleUploadedFile(
            "test.txt", b"file_content", content_type="text/plain"
        )
        response = self.client.post(
            reverse("upload"),
            {"file": uploaded_file, "selected_timestamp": "some_valid_timestamp"},
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_very_large_file(self):
        large_file_content = b"a" * (20 * 1024 * 1024)
        uploaded_file = SimpleUploadedFile(
            "large_test.txt", large_file_content, content_type="text/plain"
        )
        response = self.client.post(
            reverse("upload"),
            {"file": uploaded_file, "selected_timestamp": "some_valid_timestamp"},
        )
        self.assertEqual(response.status_code, 200)

    def test_upload_unsupported_format(self):
        uploaded_file = SimpleUploadedFile(
            "test.unsupported", b"unsupported content", content_type="text/unsupported"
        )
        response = self.client.post(
            reverse("upload"),
            {"file": uploaded_file, "selected_skip": False, "selected_timestamp": "some_valid_timestamp"},
        )
        self.assertEqual(response.status_code, 200)


class ChatGPTConvoFilterTestCase(TestCase):
    def setUp(self):
        self.file = File.objects.create(
            file="uploads/sample_file1.txt",
            title="Sample File 1",
            format="txt",
            slug="sample-file-1-" + timezone.now().strftime("%Y%m%d%H%M%S"),
        )
        self.convo = ChatGPTConvo.objects.create(file=self.file, title="Test Convo")

    def test_add_chat_filter(self):
        chat_filter, convo_filter = add_chat_filter("spam", "Filter", self.convo)
        self.assertEqual(ChatGPTFilter.objects.count(), 1)
        self.assertEqual(chat_filter.content, "spam")
        self.assertEqual(ChatGPTConvoFilter.objects.count(), 1)
        self.assertEqual(convo_filter.filter.content, "spam")


class PlotterTests(TestCase):
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("plotly.graph_objects.Figure.write_image")
    def test_plots(
        self, mock_write_image, mock_path_exists, mock_makedirs
    ):
        chat_messages = [
            {
                "Sender": "Alice",
                "Timestamp": "2024-02-10T08:00:00",
                "Message": "Hello!",
                "risk": 0,
                "PERSON": 1,
                "GPE": 0,
            },
            {
                "Sender": "Bob",
                "Timestamp": "2024-02-10T08:05:00",
                "Message": "Hi there!",
                "risk": 1,
                "PERSON": 0,
                "GPE": 1,
            },
        ]
        name = "test_plot.png"
        analysis_id = "123"

        plot_path = plots(chat_messages, name, analysis_id)
        self.assertEqual(plot_path, "vis_uploads/test_plot_plot123.png")
        mock_write_image.assert_called_once()
        expected_directory = os.getcwd()+"/media/vis_uploads"
        expected_full_path = os.path.join(expected_directory, "test_plot_plot123.png")
        mock_write_image.assert_called_with(expected_full_path)
        mock_makedirs.assert_called_once_with(expected_directory)

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("plotly.graph_objects.Figure.write_image")
    def test_plots_large_number_of_messages(
        self, mock_write_image, mock_path_exists, mock_makedirs
    ):
        chat_messages = [
            {
                "Sender": f"User{i % 3}",
                "Timestamp": f"2024-02-10T08:{i:02d}:00",
                "Message": f"Message {i}",
                "risk": 5,
                "PERSON": i % 4,
                "GPE": 5,
            }
            for i in range(60)
        ]
        name = "test_large_plot.png"
        analysis_id = "789"

        plot_path = plots(chat_messages, name, analysis_id)
        self.assertEqual(plot_path, "vis_uploads/test_large_plot_plot789.png")
        mock_write_image.assert_called_once()
        expected_directory = os. getcwd() + "/media/vis_uploads"
        expected_full_path = os.path.join(
            expected_directory, "test_large_plot_plot789.png"
        )
        mock_write_image.assert_called_with(expected_full_path)
        mock_makedirs.assert_called_once_with(expected_directory)

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    @patch("plotly.graph_objects.Figure.write_image")
    def test_plots_invalid_data(
        self, mock_write_image, mock_path_exists, mock_makedirs
    ):
        chat_messages = [{"Sender": "Alice"}]
        try:
            plot_path = plots(chat_messages, "test_invalid_data_plot.png", "112")
            self.assertIsNone(plot_path, "Plot path should be None for invalid data")
        except KeyError as e:
            self.assertIn(
                "Timestamp", str(e), "Timestamp key is missing in the input data"
            )
        mock_write_image.assert_not_called()


class Threshold:
    def __init__(self, average_risk, sentiment_multiplier, max_risk, word_risk):
        self.average_risk = average_risk
        self.sentiment_multiplier = sentiment_multiplier
        self.max_risk = max_risk
        self.word_risk = word_risk


class FileProcessTests(TestCase):
    @patch("conversation_analyst.scripts.data_ingestion.ingestion.parse_chat_file")
    @patch(
        "conversation_analyst.scripts.data_ingestion.file_process.generate_message_objects"
    )
    def test_parse_file(self, mock_generate_message_objects, mock_parse_chat_file):
        mock_file = MagicMock(spec=File)
        mock_file.title = "chat.txt"
        mock_file.file.path = "/fake/path/to/chat.txt"
        mock_parse_chat_file.return_value = [
            {"Timestamp": "2021-01-01 10:00:00", "Sender": "Alice", "Message": "Hello!"}
        ]
        parse_file(
            mock_file, date_formats=[], delimiters=[["Timestamp", ","], ["Sender", ":"]]
        )

        mock_parse_chat_file.assert_called_once_with(
            "/fake/path/to/chat.txt", [["Timestamp", ","], ["Sender", ":"]], False, []
        )
        mock_generate_message_objects.assert_called_once_with(
            mock_file, mock_parse_chat_file.return_value
        )

    @patch("conversation_analyst.scripts.data_ingestion.ingestion.parse_chat_file")
    @patch(
        "conversation_analyst.scripts.data_ingestion.file_process.generate_message_objects"
    )
    def test_parse_file_skip(self, mock_generate_message_objects, mock_parse_chat_file):
        mock_file = MagicMock(spec=File)
        mock_file.title = "chat.txt"
        mock_file.file.path = "/fake/path/to/chat.txt"
        mock_parse_chat_file.return_value = []
        parse_file(
            mock_file, date_formats=[], delimiters=[["Timestamp", ","], ["Sender", ":"]], skip=True,
        )

        mock_parse_chat_file.assert_called_once_with(
            "/fake/path/to/chat.txt", [["Timestamp", ","], ["Sender", ":"]], True, []
        )
        mock_generate_message_objects.assert_called_once_with(
            mock_file, mock_parse_chat_file.return_value
        )

    @patch("conversation_analyst.scripts.data_ingestion.file_process.tag_text")
    @patch(
        "conversation_analyst.scripts.data_ingestion.file_process.get_top_n_risk_keywords"
    )
    @patch(
        "conversation_analyst.scripts.data_ingestion.file_process.generate_analysis_objects"
    )
    def test_process_file(
        self,
        mock_generate_analysis_objects,
        mock_get_top_n_risk_keywords,
        mock_tag_text,
    ):
        mock_file = MagicMock(spec=File)
        mock_file.slug = "test-file"
        mock_messages = [
            MagicMock(
                timestamp="2021-01-01 10:00:00", sender="Alice", content="Hello", id=1
            )
        ]

        threshold_mock = Threshold(
            average_risk=0.5, sentiment_multiplier=0.7, max_risk=0.9, word_risk=1.2
        )

        mock_tag_text.return_value = ("nlp_text_mock", {"PERSON": ["Alice"], "GPE": []})

        process_file(mock_file, ["keyword1", "keyword2"], mock_messages, threshold_mock)

        # Assert test
        mock_tag_text.assert_called_once()
        mock_get_top_n_risk_keywords.assert_called_once()
        mock_generate_analysis_objects.assert_called_once()

    @patch("conversation_analyst.scripts.data_ingestion.ingestion.parse_chat_file")
    def test_process_empty_file(self, mock_parse_chat_file):
        mock_file = MagicMock(spec=File)
        mock_file.file.path = "/fake/path/to/empty_file.txt"
        mock_parse_chat_file.return_value = []

        parse_file(
            mock_file, date_formats=[], delimiters=[["Timestamp", ","], ["Sender", ":"]]
        )

    @patch("conversation_analyst.scripts.data_ingestion.ingestion.parse_chat_file")
    def test_process_corrupted_file(self, mock_parse_chat_file):
        mock_file = MagicMock(spec=File)
        mock_file.file.path = "/fake/path/to/corrupted_file.txt"
        mock_parse_chat_file.side_effect = ValueError("File format not recognized")

        with self.assertRaises(ValueError):
            parse_file(
                mock_file,
                date_formats=[],
                delimiters=[["Timestamp", ","], ["Sender", ":"]],
            )

    @patch("conversation_analyst.scripts.data_ingestion.ingestion.parse_chat_file")
    def test_process_nonexistent_file(self, mock_parse_chat_file):
        mock_file = MagicMock(spec=File)
        mock_file.file.path = "/fake/path/to/nonexistent_file.txt"
        mock_parse_chat_file.side_effect = FileNotFoundError("File not found")

        with self.assertRaises(FileNotFoundError):
            parse_file(
                mock_file,
                date_formats=[],
                delimiters=[["Timestamp", ","], ["Sender", ":"]],
            )


class TestGenerateAnalysisObjects(TestCase):
    @patch("conversation_analyst.scripts.object_creators.add_risk_word_result")
    @patch("conversation_analyst.scripts.object_creators.add_location")
    @patch("conversation_analyst.scripts.object_creators.add_person")
    @patch("conversation_analyst.scripts.object_creators.add_vis")
    @patch("conversation_analyst.scripts.object_creators.update_message")
    @patch("conversation_analyst.scripts.object_creators.add_analysis")
    @patch("conversation_analyst.scripts.data_ingestion.plotter.plots")
    def test_generate_analysis_objects(
        self,
        mock_plots,
        mock_add_analysis,
        mock_update_message,
        mock_add_vis,
        mock_add_person,
        mock_add_location,
        mock_add_risk_word_result,
    ):
        mock_file = MagicMock()
        chat_messages = [
            {
                "ObjectId": 1,
                "Sender": "Alice",
                "Timestamp": "2024-02-10T08:00:00",
                "Display_Message": "Hello",
                "Message": "Hello!",
                "risk": 0,
                "PERSON": 1,
                "GPE": 0,
                "entities": ["entity1"],
            },
            {
                "ObjectId": 2,
                "Sender": "Bob",
                "Timestamp": "2024-02-10T08:05:00",
                "Display_Message": "Hi there!",
                "Message": "Hi there!",
                "risk": 1,
                "PERSON": 0,
                "GPE": 1,
                "entities": ["entity2"],
            },
        ]
        person_and_locations = {"PERSON": ["Alice", "Bob"], "GPE": ["City1", "City2"]}
        risk_words = [("risk1", 0.5, "desc1"), ("risk2", 0.7, "desc2")]

        mock_add_analysis.return_value = MagicMock()
        mock_plots.return_value = "path/to/visualization.png"

        # Call the function under test
        generate_analysis_objects(
            mock_file,
            chat_messages,
            person_and_locations,
            risk_words,
        )

        mock_add_analysis.assert_called_once_with(mock_file)
        self.assertEqual(mock_update_message.call_count, len(chat_messages))
        mock_add_vis.assert_called_once()
        self.assertEqual(
            mock_add_person.call_count, len(person_and_locations["PERSON"])
        )
        self.assertEqual(mock_add_location.call_count, len(person_and_locations["GPE"]))
        self.assertEqual(mock_add_risk_word_result.call_count, len(risk_words))


class HomePageTests(TestCase):
    def test_homepage_without_query(self):
        client = Client()
        response = client.get(reverse("homepage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "conversation_analyst/homepage.html")

    def test_homepage_with_query(self):
        client = Client()
        response = client.get(reverse("homepage"), {"query": "Sample"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "conversation_analyst/search_result.html")

    def test_homepage_with_very_long_query(self):
        client = Client()
        long_query = "a" * 1024  # 1024 characters long
        response = client.get(reverse("homepage"), {"query": long_query})
        self.assertEqual(response.status_code, 200)

    def test_homepage_with_special_characters_in_query(self):
        client = Client()
        special_query = '!@#$%^&*()_+{}|:"<>?'
        response = client.get(reverse("homepage"), {"query": special_query})
        self.assertEqual(response.status_code, 200)

    def test_homepage_with_nonexistent_query_parameter(self):
        client = Client()
        response = client.get(reverse("homepage"), {"nonexistent": "true"})
        self.assertEqual(response.status_code, 200)


class ContentReviewTests(TestCase):
    def setUp(self):
        self.file = File.objects.create(
            file="uploads/sample_file1.txt",
            title="Sample File 1",
            format="txt",
            slug="sample-file-1-" + timezone.now().strftime("%Y%m%d%H%M%S"),
        )
        self.file.save()

    def test_content(self):
        self.file.save()
        url = reverse("content_review", kwargs={"file_slug": self.file.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_content_with_nonexistent_file_slug(self):
        nonexistent_slug = "this-slug-does-not-exist-12345"
        url = reverse("content_review", kwargs={"file_slug": nonexistent_slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("File not exist", response.content.decode())

    def test_content_with_special_character_slug(self):
        special_slug = "special-slug"
        url = reverse("content_review", kwargs={"file_slug": special_slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestTimestampParsing(unittest.TestCase):
    def test_parse_invalid_timestamp(self):
        """Test handling of an invalid timestamp format."""
        with self.assertRaises(ValueError):
            parse_timestamp("invalid-timestamp", "%Y-%m-%d %H:%M:%S")

    def test_empty_timestamp(self):
        """Test handling of an empty timestamp."""
        with self.assertRaises(ValueError):
            parse_timestamp("", "%Y-%m-%d %H:%M:%S")


class TestParseChatFile(unittest.TestCase):
    def create_temp_csv_file(self, headers, rows):
        """Create a temporary CSV file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, "w") as file:
            file.write(",".join(headers) + "\n")
            for row in rows:
                file.write(",".join(row) + "\n")
        return temp_file

    def create_temp_docx_file(self, paragraphs):
        """Create a temporary DOCX file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        doc = Document()
        for paragraph in paragraphs:
            doc.add_paragraph(paragraph)
        doc.save(temp_file.name)
        return temp_file

    def test_parse_csv_file(self):
        """Test parsing a CSV file."""
        headers = ["Timestamp", "Sender", "Message"]
        with self.assertRaises(ValueError):
            rows = [
            ]
            temp_file = self.create_temp_csv_file(headers, rows)
            parsed_data = parse_chat_file(
                temp_file.name, [["Timestamp", ","], ["Sender", ":"]], []
            )

    def test_parse_docx_file(self):
        """Test parsing a DOCX file."""
        paragraphs = [

        ]
        with self.assertRaises(ValueError):
            temp_file = self.create_temp_docx_file(paragraphs)
            parsed_data = parse_chat_file(
                temp_file.name, [["Timestamp", ","], ["Sender", ":"]], []
            )

    def create_temp_invalid_file(self, content, file_extension=".txt"):
        """Create a temporary file with invalid content and a specific extension."""
        temp_file = tempfile.NamedTemporaryFile(
            mode="w+t", suffix=file_extension, delete=False
        )
        temp_file.write(content)
        temp_file.seek(0)
        temp_file.close()
        return temp_file.name

    def test_parse_invalid_file_format(self):
        """Test parsing a file with an invalid format."""
        invalid_content = "Timestamp,Sender:Message\n2024-02-10T08:00:00,Alice:Hello\nInvalid Line Without Delimiter"
        temp_file_path = self.create_temp_invalid_file(invalid_content, ".txt")

        with self.assertRaises(ValueError) as context:
            parse_chat_file(
                temp_file_path,
                [["Timestamp", ","], ["Sender", ":"]],
                False,
                "%Y-%m-%d %H:%M:%S",
            )

        # Check if the specific error message is in the context of the exception
        self.assertIn("Pattern mismatch detected", str(context.exception))

        # Clean up by deleting the temporary file
        os.unlink(temp_file_path)


class TestCSVFileParsing(unittest.TestCase):
    def create_temp_csv_file(self, headers, rows):
        """Utility function for creating a temporary CSV file."""
        temp_file = tempfile.NamedTemporaryFile(mode="w+t", delete=False)
        writer = csv.writer(temp_file)
        writer.writerow(headers)
        writer.writerows(rows)
        temp_file.flush()
        temp_file.close()
        return temp_file.name

    def test_successful_csv_parsing(self):
        """Test parsing of a well-formed CSV
        file."""
        headers = ["Timestamp", "User", "Message"]
        rows = [
            ["2023-01-01 12:00:00", "Alice", "Hello, World!"],
            ["2023-01-02 13:30:00", "Bob", "Hi there!"],
        ]
        file_path = self.create_temp_csv_file(headers, rows)

        os.unlink(file_path)

    def test_csv_file_not_found(self):
        """Test behavior when the CSV file does not exist."""
        with self.assertRaises(ValueError) as context:
            # Ensure the file path is clearly invalid or points to a non-existing file
            parse_chat_file(
                "non_existent_file.csv",
                [["Timestamp", ","], ["Sender", ":"]],
                False,
                "%Y-%m-%d %H:%M:%S",
            )
        self.assertIn("Error reading CSV file", str(context.exception))


class ModelsTestCase(TestCase):
    def test_file_init_save(self):
        upload_file = SimpleUploadedFile("test_file.txt", b"file_content")
        file_instance = File(file=upload_file)
        file_instance.init_save()
        self.assertEqual(file_instance.title, "test_file.txt")
        self.assertEqual(file_instance.format, "txt")
        self.assertTrue(file_instance.slug.startswith(slugify(file_instance.title)))

    def test_message_set_main_sender(self):
        file_instance = File.objects.create(
            file=SimpleUploadedFile("test_file.txt", b"file_content")
        )
        message = Message.objects.create(
            file=file_instance,
            sender="Original Sender",
            main_sender="Original",
            timestamp=datetime.now(),
        )
        new_sender = "New Main Sender"
        message.set_main_sender(new_sender)
        self.assertEqual(message.main_sender, new_sender)

    def test_riskword_save(self):
        suite = KeywordSuite.objects.create(name="Suite")
        risk_word = RiskWord.objects.create(suite=suite, keyword="test")
        self.assertEqual(risk_word.lemma, get_keyword_lamma("test"))

    def test_delimiter_methods(self):
        delimiter = Delimiter.objects.create(name="Comma", value=",", order=1)
        self.assertEqual(delimiter.get_name(), "Comma")
        self.assertEqual(delimiter.get_value(), ",")
        self.assertEqual(delimiter.get_order(), 1)

    def test_analysis_str(self):
        file_instance = File.objects.create(
            file=SimpleUploadedFile("test_file.txt", b"file_content")
        )
        analysis = Analysis.objects.create(file=file_instance)
        self.assertEqual(str(analysis), str(file_instance))

    def test_riskword_result_str(self):
        riskword = RiskWord.objects.create(
            suite=KeywordSuite.objects.create(name="Suite"), keyword="test"
        )
        analysis = Analysis.objects.create(
            file=File.objects.create(
                file=SimpleUploadedFile("test_file.txt", b"file_content")
            )
        )
        result = RiskWordResult.objects.create(riskword=riskword, analysis=analysis)
        self.assertIn(str(analysis), str(result))
        self.assertIn(str(riskword), str(result))

    def test_visfile_str(self):
        file_instance = File.objects.create(
            file=SimpleUploadedFile("test_file.txt", b"file_content")
        )
        analysis = Analysis.objects.create(file=file_instance)
        visfile = VisFile.objects.create(file_path="path/to/visfile", analysis=analysis)
        self.assertEqual(str(visfile), "path/to/visfile")

    def test_dateformat_str(self):
        date_format = DateFormat.objects.create(
            name="ISO", example="2021-12-31", format="%Y-%m-%d"
        )
        self.assertEqual(str(date_format), "ISO")

    def test_delimiter_str(self):
        delimiter = Delimiter.objects.create(name="Comma", value=",")
        self.assertEqual(str(delimiter), "Comma")

    def test_chatgptconvo_save(self):
        file_instance = File.objects.create(
            file=SimpleUploadedFile("test_file.txt", b"file_content")
        )
        convo = ChatGPTConvo.objects.create(title="Initial", file=file_instance)
        self.assertIn(file_instance.title, convo.title)
        convo.init_save()
        self.assertIn(str(convo.id), convo.slug)

    def test_message_str_method(self):
        file = File.objects.create(
            file=SimpleUploadedFile("test.txt", b"dummy content")
        )
        message = Message.objects.create(
            file=file,
            timestamp=datetime.now(),
            sender="sender",
            main_sender="main_sender",
            content="This is a test message.",
            display_content="This is a test message with display content.",
            risk_rating=0,
            tags="test",
        )
        self.assertIn(message.sender, str(message))
        self.assertIn(message.timestamp.strftime("%Y-%m-%d %H:%M:%S"), str(message))

    def test_person_location_str_methods(self):
        analysis = Analysis.objects.create()
        person = Person.objects.create(name="John Doe", analysis=analysis)
        location = Location.objects.create(name="Office", analysis=analysis)
        self.assertEqual(str(person), person.name)
        self.assertEqual(str(location), location.name)

    def test_topic_str_method(self):
        topic = Topic.objects.create(name="Test Topic")
        self.assertEqual(str(topic), topic.name)

    def test_riskword_save_method(self):
        suite = KeywordSuite.objects.create(name="Suite")
        risk_word = RiskWord.objects.create(suite=suite, keyword="test")
        self.assertIsNotNone(risk_word.lemma)
