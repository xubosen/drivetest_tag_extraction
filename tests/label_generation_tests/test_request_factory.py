import pytest
import tempfile
import base64
import os
from unittest.mock import Mock
from logging import Logger

TEST_LOG_PATH = "test_logs"
TEST_DATA_DIR = "test_db/raw_db/data.json"
TEST_IMG_DIR = "test_db/raw_db/images"

# Image test constants
VALID_IMAGE_DATA = (b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H'
                    b'\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08'
                    b'\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19'
                    b'\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c'
                    b'\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00'
                    b'\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03'
                    b'\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14'
                    b'\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                    b'\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03'
                    b'\x11\x00\x3f\x00\xaa\xff\xd9')
EXPECTED_BASE64 = base64.b64encode(VALID_IMAGE_DATA).decode('utf-8')
EXPECTED_DATA_URL = f"data:image/jpeg;base64,{EXPECTED_BASE64}"

# Test constants for assign_letter_codes tests
SIMPLE_ANSWERS = {"Apple", "Banana"}
THREE_ANSWERS = {"Cat", "Dog", "Bird"}
MANY_ANSWERS = {f"Answer{i:02d}" for i in range(1, 27)}  # 26 answers (A-Z)
UNICODE_ANSWERS = {"苹果", "香蕉", "橙子"}  # Apple, Banana, Orange in Chinese
CASE_SENSITIVE_ANSWERS = {"apple", "Apple", "APPLE"}
SPECIAL_CHAR_ANSWERS = {"Answer A!", "Answer B?", "Answer C#"}

# Expected mappings for testing
EXPECTED_SIMPLE_MAPPING = {"A": "Apple", "B": "Banana"}
EXPECTED_THREE_MAPPING = {"A": "Bird", "B": "Cat", "C": "Dog"}

# Test constants for question_to_dict tests
SAMPLE_CHAPTER = (1, "Traffic Signs")
UNICODE_CHAPTER = (2, "交通规则")  # Traffic Rules in Chinese
SAMPLE_QUESTION_TEXT = "What does a red traffic light mean?"
UNICODE_QUESTION_TEXT = "红灯代表什么意思？"  # What does red light mean in Chinese
SAMPLE_CORRECT_ANSWER = "Stop"


@pytest.fixture
def mock_logger():
    """Fixture providing a mock logger for RequestFactory testing."""
    return Mock(spec=Logger)


@pytest.fixture
def request_factory(mock_logger):
    """Fixture providing a RequestFactory instance for testing."""
    from label_generator.request_factory import RequestFactory
    return RequestFactory(
        model="deepseek-r1",
        url="/v1/chat/completions",
        prompt="test prompt",
        logger=mock_logger
    )


@pytest.fixture
def sample_question():
    """Fixture providing a sample Question object for testing."""
    from entities.question import Question
    return Question(
        qid="Q001",
        chapter=SAMPLE_CHAPTER,
        question=SAMPLE_QUESTION_TEXT,
        answers=SIMPLE_ANSWERS,
        correct_answer=SAMPLE_CORRECT_ANSWER
    )


@pytest.fixture
def unicode_question():
    """Fixture providing a Question object with unicode characters."""
    from entities.question import Question
    return Question(
        qid="Q002",
        chapter=UNICODE_CHAPTER,
        question=UNICODE_QUESTION_TEXT,
        answers=UNICODE_ANSWERS,
        correct_answer="苹果"
    )


@pytest.fixture
def question_with_many_answers():
    """Fixture providing a Question object with many answer choices."""
    from entities.question import Question
    return Question(
        qid="Q003",
        chapter=SAMPLE_CHAPTER,
        question=SAMPLE_QUESTION_TEXT,
        answers=MANY_ANSWERS,
        correct_answer=list(MANY_ANSWERS)[0]
    )


@pytest.fixture
def question_with_image(temp_image_file):
    """Fixture providing a Question object with an image for testing."""
    from entities.question import Question
    return Question(
        qid="Q004",
        chapter=SAMPLE_CHAPTER,
        question=SAMPLE_QUESTION_TEXT,
        answers=SIMPLE_ANSWERS,
        correct_answer=SAMPLE_CORRECT_ANSWER,
        img_path=temp_image_file
    )


@pytest.fixture
def temp_image_file():
    """Fixture providing a temporary valid image file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file.write(VALID_IMAGE_DATA)
        temp_file_path = temp_file.name

    yield temp_file_path

    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def temp_empty_file():
    """Fixture providing a temporary empty file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file_path = temp_file.name

    yield temp_file_path

    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


class TestRequestFactoryInitialization:
    """Test suite for RequestFactory constructor and initialization."""

    def test_valid_initialization_success(self):
        """Test that RequestFactory initializes correctly with valid
        parameters."""
        from label_generator.request_factory import RequestFactory
        from unittest.mock import Mock
        from logging import Logger

        mock_logger = Mock(spec=Logger)
        factory = RequestFactory(
            model="test-model",
            url="/v1/chat/completions",
            prompt="test prompt",
            logger=mock_logger
        )

        assert factory._model == "test-model"
        assert factory._url == "/v1/chat/completions"
        assert factory._prompt == "test prompt"
        assert factory._logger == mock_logger


class TestMakeRequestMethod:
    """Test suite for the make_request public method."""

    def _assert_basic_request_structure(self, request, expected_custom_id):
        """Helper method to assert basic request structure and properties."""
        from label_generator.basic_labeling_request import BasicLabelingRequest

        assert isinstance(request, BasicLabelingRequest)
        assert request.custom_id == expected_custom_id
        assert request.model == "deepseek-r1"
        assert request.url == "/v1/chat/completions"
        assert request.prompt == "test prompt"
        assert isinstance(request.content, list)
        assert len(request.content) > 0

    def test_make_request_text_only_question_success(self, request_factory,
                                                     sample_question):
        """Test that make_request creates a valid BasicLabelingRequest for
        text-only questions."""
        custom_id = "test_custom_id_001"

        request = request_factory.make_request(sample_question, custom_id)

        self._assert_basic_request_structure(request, custom_id)

        # Should have only one content item for text-only questions
        assert len(request.content) == 1
        assert request.content[0]["type"] == "text"
        assert "text" in request.content[0]

        # Verify that question data is properly formatted in the text
        text_content = request.content[0]["text"]
        assert SAMPLE_QUESTION_TEXT in text_content
        assert SAMPLE_CORRECT_ANSWER in text_content

    def test_make_request_question_with_image_success(self, request_factory,
                                                      question_with_image):
        """Test that make_request creates a valid BasicLabelingRequest for
        questions with images."""
        custom_id = "test_custom_id_002"

        request = request_factory.make_request(question_with_image, custom_id)

        self._assert_basic_request_structure(request, custom_id)

        # Should have two content items for questions with images
        assert len(request.content) == 2

        # First item should be the image
        assert request.content[0]["type"] == "image_url"
        assert "image_url" in request.content[0]

        # Second item should be the text
        assert request.content[1]["type"] == "text"
        assert "text" in request.content[1]

        # Verify that question data is properly formatted in the text
        text_content = request.content[1]["text"]
        assert SAMPLE_QUESTION_TEXT in text_content

    def test_make_request_returns_correct_type(self, request_factory,
                                               sample_question):
        """Test that make_request returns a BasicLabelingRequest instance."""
        from label_generator.basic_labeling_request import BasicLabelingRequest

        request = request_factory.make_request(sample_question, "test_id")

        assert isinstance(request, BasicLabelingRequest)
        assert hasattr(request, 'custom_id')
        assert hasattr(request, 'model')
        assert hasattr(request, 'url')
        assert hasattr(request, 'prompt')
        assert hasattr(request, 'content')

    def test_make_request_uses_provided_custom_id(self, request_factory,
                                                  sample_question):
        """Test that make_request uses the provided custom_id in the returned
        request."""
        test_custom_ids = [
            "simple_id",
            "id_with_underscores",
            "id-with-dashes",
            "id123with456numbers",
            "very_long_custom_id_with_many_characters_to_test_length_handling"
        ]

        for custom_id in test_custom_ids:
            request = request_factory.make_request(sample_question, custom_id)
            assert request.custom_id == custom_id

    def test_make_request_with_none_question_fails(self, request_factory):
        """Test that make_request fails when question parameter is None."""
        with pytest.raises(AttributeError):
            request_factory.make_request(None, "test_id")

    def test_make_request_with_none_custom_id_fails(self, request_factory,
                                                    sample_question):
        """Test that make_request fails when custom_id parameter is None."""
        with pytest.raises(ValueError):
            request_factory.make_request(sample_question, None)

    def test_make_request_with_empty_custom_id_fails(self, request_factory,
                                                     sample_question):
        """Test that make_request fails when custom_id parameter is empty
        string."""
        with pytest.raises(ValueError):
            request_factory.make_request(sample_question, "")


class TestMakeContentMethod:
    """Test suite for the _make_content private method."""

    def _call_make_content(self, request_factory, question):
        """Helper method to call the private _make_content method."""
        return request_factory._make_content(question)

    def test_make_content_text_only_question_structure(self, request_factory,
                                                       sample_question):
        """Test that _make_content returns correct structure for text-only
        questions."""
        result = self._call_make_content(request_factory, sample_question)

        assert isinstance(result, list)
        assert len(result) == 1

        # Should have a single text content item
        content_item = result[0]
        assert isinstance(content_item, dict)
        assert content_item["type"] == "text"
        assert "text" in content_item
        assert isinstance(content_item["text"], str)
        assert len(content_item["text"]) > 0

        # Verify question data is included in text
        text_content = content_item["text"]
        assert SAMPLE_QUESTION_TEXT in text_content
        assert SAMPLE_CORRECT_ANSWER in text_content

    def test_make_content_question_with_image_structure(self, request_factory,
                                                        question_with_image):
        """Test that _make_content returns correct structure for questions
        with images."""
        result = self._call_make_content(request_factory, question_with_image)

        assert isinstance(result, list)
        assert len(result) == 2

        # First item should be an image
        image_item = result[0]
        assert isinstance(image_item, dict)
        assert image_item["type"] == "image_url"
        assert "image_url" in image_item
        assert isinstance(image_item["image_url"], str)
        assert image_item["image_url"].startswith("data:image/jpeg;base64,")

        # Second item should be text
        text_item = result[1]
        assert isinstance(text_item, dict)
        assert text_item["type"] == "text"
        assert "text" in text_item
        assert isinstance(text_item["text"], str)
        assert len(text_item["text"]) > 0

        # Verify question data is included in text
        text_content = text_item["text"]
        assert SAMPLE_QUESTION_TEXT in text_content


class TestFormatTextMethod:
    """Test suite for the _format_text private method."""

    def _call_format_text(self, request_factory, question):
        """Helper method to call the private _format_text method."""
        return request_factory._format_text(question)

    def test_format_text_returns_string(self, request_factory, sample_question):
        """Test that _format_text returns a string representation."""
        result = self._call_format_text(request_factory, sample_question)

        assert isinstance(result, str)
        assert len(result) > 0

        # Verify it contains expected question data
        assert SAMPLE_QUESTION_TEXT in result
        assert SAMPLE_CORRECT_ANSWER in result

        # Verify it contains Chinese keys from _question_to_dict
        assert "章节" in result
        assert "题目" in result
        assert "选项" in result
        assert "答案" in result

    def test_format_text_with_none_question_fails(self, request_factory):
        """Test that _format_text fails when question parameter is None."""
        with pytest.raises(AttributeError):
            self._call_format_text(request_factory, None)

    def test_format_text_handles_unicode_characters(self, request_factory,
                                                    unicode_question):
        """Test that _format_text correctly handles unicode characters in
        question data."""
        result = self._call_format_text(request_factory, unicode_question)

        assert isinstance(result, str)
        assert len(result) > 0

        # Verify unicode question text is preserved
        assert UNICODE_QUESTION_TEXT in result

        # Verify unicode chapter name is preserved
        assert "交通规则" in result

        # Verify unicode answers are preserved
        assert "苹果" in result
        assert "香蕉" in result
        assert "橙子" in result


class TestFormatImageMethod:
    """Test suite for the _format_image private method."""

    def _call_format_image(self, request_factory, img_path):
        """Helper method to call the private _format_image method."""
        return request_factory._format_image(img_path)

    def test_format_image_valid_file_success(self, request_factory,
                                             temp_image_file):
        """Test that _format_image successfully encodes a valid image file."""
        result = self._call_format_image(request_factory, temp_image_file)

        assert isinstance(result, str)
        assert len(result) > 0
        assert result.startswith("data:image/jpeg;base64,")

    def test_format_image_returns_data_url_format(self, request_factory,
                                                  temp_image_file):
        """Test that _format_image returns image in data URL format."""
        result = self._call_format_image(request_factory, temp_image_file)

        assert result.startswith("data:image/jpeg;base64,")

        # Verify the format is correct
        parts = result.split(',', 1)
        assert len(parts) == 2
        assert parts[0] == "data:image/jpeg;base64"

        # Verify the base64 part is valid
        try:
            base64.b64decode(parts[1])
        except Exception:
            pytest.fail("Invalid base64 encoding in data URL")

    def test_format_image_file_not_found_raises_value_error(self,
                                                            request_factory):
        """Test that _format_image raises ValueError when file doesn't exist."""
        non_existent_path = "/non/existent/path/image.jpg"

        with pytest.raises(ValueError) as exc_info:
            self._call_format_image(request_factory, non_existent_path)

        assert "No such file or directory" in str(exc_info.value)
        assert non_existent_path in str(exc_info.value)

    def test_format_image_empty_file_handles_gracefully(self, request_factory,
                                                        temp_empty_file):
        """Test that _format_image handles empty image files gracefully."""
        result = self._call_format_image(request_factory, temp_empty_file)

        # Should still return a valid data URL format, just with empty base64
        # content
        assert result == "data:image/jpeg;base64,"

    def test_format_image_with_none_path_fails(self, request_factory):
        """Test that _format_image fails when image path is None."""
        with pytest.raises(ValueError):
            self._call_format_image(request_factory, None)

    def test_format_image_with_empty_path_fails(self, request_factory):
        """Test that _format_image fails when image path is empty string."""
        with pytest.raises(ValueError) as exc_info:
            self._call_format_image(request_factory, "")

        assert "No such file or directory" in str(exc_info.value)

    def test_format_image_base64_encoding_correctness(self, request_factory,
                                                      temp_image_file):
        """Test that _format_image produces correct base64 encoding."""
        result = self._call_format_image(request_factory, temp_image_file)

        # Extract the base64 part
        base64_part = result.split(',', 1)[1]

        # Decode and compare with original file content
        decoded_data = base64.b64decode(base64_part)

        with open(temp_image_file, 'rb') as f:
            original_data = f.read()

        assert decoded_data == original_data
        assert decoded_data == VALID_IMAGE_DATA


class TestRequestFactoryIntegration:
    """Test suite for integration scenarios and end-to-end workflows."""
    # TODO: Implement integration tests for the complete workflow

    def test_full_workflow_text_only_question(self):
        """Test complete workflow from factory creation to request generation
        for text-only questions."""

    def test_full_workflow_question_with_image(self):
        """Test complete workflow from factory creation to request generation
        for questions with images."""

    def test_multiple_requests_same_factory(self):
        """Test that the same factory can generate multiple requests
        correctly."""


class TestRequestFactoryErrorHandling:
    """Test suite for error handling and exception scenarios."""
    # TODO: Implement error handling tests

    def test_error_propagation_through_workflow(self):
        """Test that errors are properly propagated through the complete
        workflow."""

    def test_file_system_errors_during_image_processing(self):
        """Test handling of file system errors during image encoding."""

    def test_corrupted_image_file_handling(self):
        """Test handling of corrupted or invalid image files."""
