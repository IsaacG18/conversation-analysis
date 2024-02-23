from django.test import TestCase, Client
from django.urls import reverse
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
)
from .scripts.nlp.nlp import (
    classify,
    get_top_n_risk_keywords,
    label_entity,
    label_keyword,
    message_to_text,
    create_arrays,
    get_date_messages,
    get_keyword_lamma,
    tag_text,
    name_location_chatgpt
)
from django.utils import timezone
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
from .scripts.data_ingestion.file_process import parse_file, process_file
import os
import numpy as np
import spacy

nlp = spacy.load("en_core_web_md")


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
        ct = add_custom_threshold(average_risk=0.8, sentiment_multiplier=2, max_risk=40, word_risk=7)
        self.assertEqual(CustomThresholds.objects.count(), 1)
        self.assertEqual(ct.average_risk, 0.8)
        self.assertEqual(ct.sentiment_multiplier, 2)
        self.assertEqual(ct.max_risk, 40)
        self.assertEqual(ct.word_risk, 7)


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

    def test_create_arrays(self):
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
        date_messages = create_arrays(parsed_data)
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
        names, locations = name_location_chatgpt("Hello, I am Isaac, and I am from Dundee")
        self.assertEqual(1, len(names))
        self.assertEqual(1, len(locations))
        self.assertEqual("Isaac", names[0])
        self.assertEqual("Dundee", locations[0])


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


# class ChatGPTFilteringTestCase(TestCase):
#     def setUp(self):
#         test_file = File.objects.create(file='path/to/file', title='Test File', format='txt', slug='test-file-'
#             + timezone.now().strftime("%Y%m%d%H%M%S"))
#         date_today = timezone.now()
#         ChatGPTConvo.objects.create(title="Conversation Today", file=test_file, date=date_today)
#         ChatGPTConvo.objects.create(title="Conversation Yesterday", file=test_file, date=date_today - timedelta(days=1))
#         ChatGPTConvo.objects.create(title="Conversation Last Week", file=test_file, date=date_today - timedelta(weeks=1))

#     def test_filter_conversations_by_date_range(self):
#         """Test filtering conversations within a specific date range."""
#         date_today = timezone.now()
#         start_date = date_today - timedelta(days=2)
#         end_date = date_today
#         conversations = ChatGPTConvo.objects.filter(date__range=(start_date, end_date))

#         # Verify that only conversations within the last 2 days are returned
#         self.assertEqual(conversations.count(), 2)
#         self.assertTrue(any(convo.title == "Conversation Today" for convo in conversations))
#         self.assertTrue(any(convo.title == "Conversation Yesterday" for convo in conversations))


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
    @patch("os.getcwd", return_value="/fake/directory")
    @patch("plotly.graph_objects.Figure.write_image")
    def test_plots(
        self, mock_write_image, mock_getcwd, mock_path_exists, mock_makedirs
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
        expected_directory = "/fake/directory/media/vis_uploads"
        expected_full_path = os.path.join(expected_directory, "test_plot_plot123.png")
        mock_write_image.assert_called_with(expected_full_path)
        mock_makedirs.assert_called_once_with(expected_directory)


class Threshold:
    def __init__(self, average_risk, sentiment_divider, max_risk, word_risk):
        self.average_risk = average_risk
        self.sentiment_divider = sentiment_divider
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
            "/fake/path/to/chat.txt", [["Timestamp", ","], ["Sender", ":"]], []
        )
        mock_generate_message_objects.assert_called_once_with(
            mock_file, mock_parse_chat_file.return_value
        )

    @patch("conversation_analyst.scripts.data_ingestion.file_process.create_arrays")
    @patch("conversation_analyst.scripts.data_ingestion.file_process.tag_text")
    @patch(
        "conversation_analyst.scripts.data_ingestion.file_process.get_top_n_risk_keywords"
    )
    @patch(
        "conversation_analyst.scripts.data_ingestion.file_process.get_top_n_common_topics_with_avg_risk"
    )
    @patch(
        "conversation_analyst.scripts.data_ingestion.file_process.generate_analysis_objects"
    )
    def test_process_file(
        self,
        mock_generate_analysis_objects,
        mock_get_top_n_common_topics_with_avg_risk,
        mock_get_top_n_risk_keywords,
        mock_tag_text,
        mock_create_arrays,
    ):
        mock_file = MagicMock(spec=File)
        mock_file.slug = "test-file"
        mock_messages = [
            MagicMock(
                timestamp="2021-01-01 10:00:00", sender="Alice", content="Hello", id=1
            )
        ]
        chat_messages = [
            {
                "Timestamp": "2021-01-01 10:00:00",
                "Sender": "Alice",
                "Message": "Hello",
                "ObjectId": 1,
            }
        ]
        threshold_mock = Threshold(
            average_risk=0.5, sentiment_multiplier=0.7, max_risk=0.9, word_risk=1.2
        )

        mock_tag_text.return_value = ("nlp_text_mock", {"PERSON": ["Alice"], "GPE": []})

        process_file(mock_file, ["keyword1", "keyword2"], mock_messages, threshold_mock)

        # Assert test
        mock_create_arrays.assert_called_once_with(chat_messages)
        mock_tag_text.assert_called_once()
        mock_get_top_n_risk_keywords.assert_called_once()
        mock_get_top_n_common_topics_with_avg_risk.assert_called_once()
        mock_generate_analysis_objects.assert_called_once()


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
