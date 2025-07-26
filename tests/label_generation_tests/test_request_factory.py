import pytest
from unittest.mock import Mock
from logging import Logger

TEST_LOG_PATH = "test_logs"

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
        model="test-model",
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


class TestRequestFactoryInitialization:
    """Test suite for RequestFactory constructor and initialization."""

    def test_valid_initialization_success(self):
        """Test that RequestFactory initializes correctly with valid parameters."""


class TestMakeRequestMethod:
    """Test suite for the make_request public method."""

    def test_make_request_text_only_question_success(self):
        """Test that make_request creates a valid BasicLabelingRequest for text-only questions."""

    def test_make_request_question_with_image_success(self):
        """Test that make_request creates a valid BasicLabelingRequest for questions with images."""

    def test_make_request_returns_correct_type(self):
        """Test that make_request returns a BasicLabelingRequest instance."""

    def test_make_request_uses_provided_custom_id(self):
        """Test that make_request uses the provided custom_id in the returned request."""

    def test_make_request_with_none_question_fails(self):
        """Test that make_request fails when question parameter is None."""

    def test_make_request_with_none_custom_id_fails(self):
        """Test that make_request fails when custom_id parameter is None."""

    def test_make_request_with_empty_custom_id_fails(self):
        """Test that make_request fails when custom_id parameter is empty string."""


class TestMakeContentMethod:
    """Test suite for the _make_content private method."""

    def test_make_content_text_only_question_structure(self):
        """Test that _make_content returns correct structure for text-only questions."""

    def test_make_content_question_with_image_structure(self):
        """Test that _make_content returns correct structure for questions with images."""


class TestFormatTextMethod:
    """Test suite for the _format_text private method."""

    def test_format_text_returns_string(self):
        """Test that _format_text returns a string representation."""

    def test_format_text_with_none_question_fails(self):
        """Test that _format_text fails when question parameter is None."""

    def test_format_text_handles_unicode_characters(self):
        """Test that _format_text correctly handles unicode characters in question data."""


class TestFormatImageMethod:
    """Test suite for the _format_image private method."""

    def test_format_image_valid_file_success(self):
        """Test that _format_image successfully encodes a valid image file."""

    def test_format_image_returns_data_url_format(self):
        """Test that _format_image returns image in data URL format."""

    def test_format_image_file_not_found_raises_value_error(self):
        """Test that _format_image raises ValueError when file doesn't exist."""

    def test_format_image_empty_file_handles_gracefully(self):
        """Test that _format_image handles empty image files gracefully."""

    def test_format_image_with_none_path_fails(self):
        """Test that _format_image fails when image path is None."""

    def test_format_image_with_empty_path_fails(self):
        """Test that _format_image fails when image path is empty string."""

    def test_format_image_base64_encoding_correctness(self):
        """Test that _format_image produces correct base64 encoding."""


class TestQuestionToDictMethod:
    """Test suite for the _question_to_dict private method."""

    def _call_question_to_dict(self, request_factory, question):
        """Helper method to call the private _question_to_dict method."""
        return request_factory._question_to_dict(question)

    def test_question_to_dict_returns_correct_structure(self, request_factory, sample_question):
        """Test that _question_to_dict returns dictionary with expected keys."""
        result = self._call_question_to_dict(request_factory, sample_question)

        assert isinstance(result, dict)
        expected_keys = {"章节", "题目", "选项", "答案"}
        assert set(result.keys()) == expected_keys

    def test_question_to_dict_chapter_format_correct(self, request_factory, sample_question):
        """Test that _question_to_dict formats chapter as 'number: name'."""
        result = self._call_question_to_dict(request_factory, sample_question)

        expected_chapter = f"{SAMPLE_CHAPTER[0]}: {SAMPLE_CHAPTER[1]}"
        assert result["章节"] == expected_chapter

    def test_question_to_dict_question_text_unchanged(self, request_factory, sample_question):
        """Test that _question_to_dict preserves original question text."""
        result = self._call_question_to_dict(request_factory, sample_question)

        assert result["题目"] == SAMPLE_QUESTION_TEXT

    def test_question_to_dict_options_are_lettered(self, request_factory, sample_question):
        """Test that _question_to_dict assigns letter codes to answer options."""
        result = self._call_question_to_dict(request_factory, sample_question)

        options = result["选项"]
        assert isinstance(options, dict)
        assert set(options.keys()) == {"A", "B"}
        assert set(options.values()) == SIMPLE_ANSWERS

    def test_question_to_dict_answer_unchanged(self, request_factory, sample_question):
        """Test that _question_to_dict preserves correct answer text."""
        result = self._call_question_to_dict(request_factory, sample_question)

        assert result["答案"] == SAMPLE_CORRECT_ANSWER

    def test_question_to_dict_with_none_question_fails(self, request_factory):
        """Test that _question_to_dict fails when question parameter is None."""
        with pytest.raises(AttributeError):
            self._call_question_to_dict(request_factory, None)

    def test_question_to_dict_handles_exception_gracefully(self, request_factory, mock_logger):
        """Test that _question_to_dict handles exceptions and logs errors appropriately."""
        from unittest.mock import Mock

        # Create a mock question that will raise an exception
        mock_question = Mock()
        mock_question.get_qid.return_value = "Q999"
        mock_question.get_chapter.side_effect = Exception("Test exception")

        with pytest.raises(ValueError) as exc_info:
            self._call_question_to_dict(request_factory, mock_question)

        # Verify error message contains question ID
        assert "Q999" in str(exc_info.value)

        # Verify logger was called with error
        mock_logger.error.assert_called_once()
        error_call_args = mock_logger.error.call_args[0][0]
        assert "Q999" in error_call_args

    def test_question_to_dict_unicode_chapter_handling(self, request_factory, unicode_question):
        """Test that _question_to_dict correctly handles unicode characters in chapter names."""
        result = self._call_question_to_dict(request_factory, unicode_question)

        expected_chapter = f"{UNICODE_CHAPTER[0]}: {UNICODE_CHAPTER[1]}"
        assert result["章节"] == expected_chapter
        assert result["题目"] == UNICODE_QUESTION_TEXT

        # Verify unicode characters are preserved in all fields
        assert "交通规则" in result["章节"]
        assert "红灯代表什么意思" in result["题目"]


class TestAssignLetterCodesMethod:
    """Test suite for the _assign_letter_codes private method."""

    def _call_assign_letter_codes(self, request_factory, answer_choices):
        """Helper method to call the private _assign_letter_codes method."""
        return request_factory._assign_letter_codes(answer_choices)

    def test_assign_letter_codes_returns_dictionary(self, request_factory):
        """Test that _assign_letter_codes returns a dictionary mapping letters to answers."""
        result = self._call_assign_letter_codes(request_factory, SIMPLE_ANSWERS)

        assert isinstance(result, dict)
        assert len(result) == len(SIMPLE_ANSWERS)

    def test_assign_letter_codes_starts_with_letter_a(self, request_factory):
        """Test that _assign_letter_codes starts letter assignment with 'A'."""
        result = self._call_assign_letter_codes(request_factory, SIMPLE_ANSWERS)

        assert "A" in result
        assert list(result.keys())[0] == "A"

    def test_assign_letter_codes_sequential_letters(self, request_factory):
        """Test that _assign_letter_codes assigns letters in sequential order (A, B, C, ...)."""
        result = self._call_assign_letter_codes(request_factory, THREE_ANSWERS)

        expected_letters = ["A", "B", "C"]
        actual_letters = list(result.keys())

        assert actual_letters == expected_letters

    def test_assign_letter_codes_preserves_answer_text(self, request_factory):
        """Test that _assign_letter_codes preserves original answer text as values."""
        result = self._call_assign_letter_codes(request_factory, SIMPLE_ANSWERS)

        # Check all original answers are preserved as values
        result_values = set(result.values())
        assert result_values == SIMPLE_ANSWERS

    def test_assign_letter_codes_sorts_answers_alphabetically(self, request_factory):
        """Test that _assign_letter_codes sorts answers alphabetically before assigning letters."""
        result = self._call_assign_letter_codes(request_factory, SIMPLE_ANSWERS)

        # Expected mapping based on alphabetical sorting
        assert result == EXPECTED_SIMPLE_MAPPING

        # Test with three answers to verify sorting
        result_three = self._call_assign_letter_codes(request_factory, THREE_ANSWERS)
        assert result_three == EXPECTED_THREE_MAPPING

    def test_assign_letter_codes_two_answers(self, request_factory):
        """Test that _assign_letter_codes handles exactly two answer choices correctly."""
        result = self._call_assign_letter_codes(request_factory, SIMPLE_ANSWERS)

        assert len(result) == 2
        assert set(result.keys()) == {"A", "B"}
        assert result == EXPECTED_SIMPLE_MAPPING

    def test_assign_letter_codes_many_answers(self, request_factory):
        """Test that _assign_letter_codes handles many answer choices (up to Z)."""
        result = self._call_assign_letter_codes(request_factory, MANY_ANSWERS)

        assert len(result) == 26

        # Check all letters A-Z are used
        expected_letters = [chr(ord('A') + i) for i in range(26)]
        assert list(result.keys()) == expected_letters

        # Check all answers are preserved
        assert set(result.values()) == MANY_ANSWERS

    def test_assign_letter_codes_empty_set_returns_empty_dict(self, request_factory):
        """Test that _assign_letter_codes returns empty dictionary for empty answer set."""
        result = self._call_assign_letter_codes(request_factory, set())

        assert result == {}
        assert isinstance(result, dict)

    def test_assign_letter_codes_with_none_answers_fails(self, request_factory):
        """Test that _assign_letter_codes fails when answer_choices parameter is None."""
        with pytest.raises((TypeError, AttributeError)):
            self._call_assign_letter_codes(request_factory, None)

    def test_assign_letter_codes_unicode_answers(self, request_factory):
        """Test that _assign_letter_codes correctly handles unicode characters in answers."""
        result = self._call_assign_letter_codes(request_factory, UNICODE_ANSWERS)

        assert len(result) == 3
        assert set(result.values()) == UNICODE_ANSWERS

        # Check that unicode characters are preserved correctly
        for value in result.values():
            assert value in UNICODE_ANSWERS

    def test_assign_letter_codes_case_sensitive_sorting(self, request_factory):
        """Test that _assign_letter_codes sorts answers in case-sensitive manner."""
        result = self._call_assign_letter_codes(request_factory, CASE_SENSITIVE_ANSWERS)

        # Python's sorted() is case-sensitive by default (uppercase before lowercase)
        sorted_answers = sorted(list(CASE_SENSITIVE_ANSWERS))
        expected_mapping = {chr(ord('A') + i): answer for i, answer in enumerate(sorted_answers)}

        assert result == expected_mapping
        assert len(result) == 3

    def test_assign_letter_codes_special_characters(self, request_factory):
        """Test that _assign_letter_codes handles answers with special characters correctly."""
        result = self._call_assign_letter_codes(request_factory, SPECIAL_CHAR_ANSWERS)

        assert len(result) == 3
        assert set(result.values()) == SPECIAL_CHAR_ANSWERS

        # Verify all answers with special characters are preserved
        for value in result.values():
            assert any(char in value for char in "!?#")


class TestRequestFactoryIntegration:
    """Test suite for integration scenarios and end-to-end workflows."""

    def test_full_workflow_text_only_question(self):
        """Test complete workflow from factory creation to request generation for text-only questions."""

    def test_full_workflow_question_with_image(self):
        """Test complete workflow from factory creation to request generation for questions with images."""

    def test_multiple_requests_same_factory(self):
        """Test that the same factory can generate multiple requests correctly."""

    def test_error_propagation_through_workflow(self):
        """Test that errors are properly propagated through the complete workflow."""


class TestRequestFactoryEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_question_with_missing_chapter_information(self):
        """Test handling of questions with None or invalid chapter information."""

    def test_question_with_maximum_answer_choices(self):
        """Test handling of questions with maximum possible answer choices (26+)."""

    def test_image_path_with_special_characters(self):
        """Test handling of image paths containing special characters."""

    def test_factory_reuse_after_errors(self):
        """Test that factory can be reused successfully after encountering errors."""


class TestRequestFactoryErrorHandling:
    """Test suite for error handling and exception scenarios."""

    def test_file_system_errors_during_image_processing(self):
        """Test handling of file system errors during image encoding."""

    def test_corrupted_image_file_handling(self):
        """Test handling of corrupted or invalid image files."""
