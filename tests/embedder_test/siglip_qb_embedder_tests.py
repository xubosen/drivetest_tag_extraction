# Unit tests for the QBEmbedder class and its helper functions.

# Library Imports
import pytest
import numpy as np
import logging
from logging import Logger
import os
from datetime import datetime
from unittest.mock import Mock, patch
import torch
from transformers.models.siglip2.modeling_siglip2 import Siglip2Model
from transformers.models.siglip2.processing_siglip2 import Siglip2Processor

# Local Imports
from qb.question_bank import QuestionBank
from qb.question import Question
from embedder.siglip2_qb_embedder import Siglip2QBEmbedder, _has_image, _format_question
from data_storage.database.json_database import LocalJsonDB

# Constants for testing
FILE_PATH = "test_db/db_file.json"
IMG_DIR = "test_db/img"
LOG_DIR = "test_logs"

# Helper functions for testing
def _make_logger() -> Logger:
    """ Return a logger for debugging. """
    # Create the logger
    logger = logging.getLogger("test_qb_embedder")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers if any
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"qb_embedder_test_{timestamp}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def _get_qb() -> QuestionBank:
    """ Return a sample question bank for testing. """
    db = LocalJsonDB(FILE_PATH, IMG_DIR)
    return db.load()

def _make_fake_model() -> tuple[Mock, Mock]:
    """ Return a mock model for testing. """
    model_mock = Mock(spec=Siglip2Model)
    processor_mock = Mock(spec=Siglip2Processor)

    # Configure processor mock to return a dictionary when called
    processor_mock.return_value = {
        "input_ids": torch.ones((1, 10), dtype=torch.long),
        "attention_mask": torch.ones((1, 10), dtype=torch.long),
        "pixel_values": torch.ones((1, 3, 224, 224), dtype=torch.float)
    }

    # Configure model mock to return an object with text_embeds and image_embeds attributes
    output_mock = Mock()
    output_mock.text_embeds = torch.ones((1, 768), dtype=torch.float)
    output_mock.image_embeds = torch.ones((1, 768), dtype=torch.float)
    output_mock.text = torch.ones((1, 768), dtype=torch.float)
    model_mock.return_value = output_mock

    return model_mock, processor_mock

# ========= Tests =========
class TestHelperFunctions:
    """Tests for the helper functions outside the QBEmbedder class."""

    def test_has_image_with_image(self):
        """Test _has_image returns True when a question has an image."""
        # Create a question with an image path
        question = Mock(spec=Question)
        question.get_img_path.return_value = "path/to/image.jpg"

        # Test the function
        result = _has_image(question)

        # Assert
        assert result is True
        question.get_img_path.assert_called_once()

    def test_has_image_without_image(self):
        """Test _has_image returns False when a question has no image."""
        # Create a question without an image path
        question = Mock(spec=Question)
        question.get_img_path.return_value = None

        # Test the function
        result = _has_image(question)

        # Assert
        assert result is False
        question.get_img_path.assert_called_once()

    def test_format_question_format(self):
        """Test _format_question correctly formats a question."""
        # Create a question
        question = Mock(spec=Question)
        question.get_question.return_value = "What is the capital of Canada?"
        question.get_correct_answer.return_value = "Ottawa"

        # Define a chapter
        chapter = "Geography"

        # Expected formatted string
        expected = "章节: Geography\n题目: What is the capital of Canada?\n答案: Ottawa"

        # Test the function
        result = _format_question(question, chapter)

        # Assert
        assert result == expected
        question.get_question.assert_called_once()
        question.get_correct_answer.assert_called_once()

    def test_format_question_with_special_characters(self):
        """Test _format_question handles special characters correctly."""
        # Create a question with special characters
        question = Mock(spec=Question)
        question.get_question.return_value = "这是一个中文问题 with special chars: &$#@!?"
        question.get_correct_answer.return_value = "答案是: 42! (四十二)"

        # Define a chapter with special characters
        chapter = "测试章节 123"

        # Expected formatted string
        expected = (
            "章节: 测试章节 123\n"
            "题目: 这是一个中文问题 with special chars: &$#@!?\n"
            "答案: 答案是: 42! (四十二)"
        )

        # Test the function
        result = _format_question(question, chapter)

        # Assert
        assert result == expected
        question.get_question.assert_called_once()
        question.get_correct_answer.assert_called_once()


class TestQBEmbedderInitialization:
    """Tests for QBEmbedder initialization."""

    def test_init_with_valid_parameters(self):
        """Test QBEmbedder initialization with a model and logger."""
        # Create mock objects
        mock_model, mock_processor = _make_fake_model()
        mock_logger = Mock(spec=Logger)

        # Initialize the embedder
        embedder = Siglip2QBEmbedder(
            model=mock_model,
            processor=mock_processor,
            logger=mock_logger
        )

        # Assert instance variables are correctly set
        assert embedder._model is mock_model
        assert embedder._processor is mock_processor
        assert embedder._logger is mock_logger

        # Verify no methods were called during initialization
        mock_model.assert_not_called()
        mock_processor.assert_not_called()
        mock_logger.assert_not_called()


class TestEncodeQB:
    """Tests for the encode_qb method."""

    def test_encode_qb_single_chapter_no_images(self):
        """Test encoding a question bank with a single chapter and no images."""
        pass

    def test_encode_qb_multiple_chapters(self):
        """Test encoding a question bank with multiple chapters."""
        pass

    def test_encode_qb_with_images(self):
        """Test encoding a question bank containing questions with images."""
        pass

    def test_encode_qb_mixed_questions(self):
        """Test encoding a question bank with a mix of questions with and without images."""
        pass

    def test_encode_qb_returns_correct_shape(self):
        """Test that encode_qb returns an array of the correct shape."""
        pass


class TestEncodeQuestion:
    """Tests for the _encode_question method."""

    def test_encode_question_without_image(self):
        """Test encoding a question without an image."""
        pass

    def test_encode_question_with_image(self):
        """Test encoding a question with an image."""
        pass


class TestEncodeTextAndImage:
    """Tests for the _encode_text_and_img method."""

    def test_encode_text_and_img_averaging(self):
        """Test that _encode_text_and_img correctly averages text and image embeddings."""
        pass


class TestEncodeText:
    """Tests for the _encode_text method."""

    def test_encode_text_returns_tensor(self):
        """Test that _encode_text returns a tensor with correct shape."""
        # Create mock objects but use a real logger
        mock_model, mock_processor = _make_fake_model()
        real_logger = _make_logger()

        # Set expected output shape
        expected_shape = (1, 768)
        expected_output = torch.ones(expected_shape, dtype=torch.float)
        mock_model.return_value.text = expected_output

        # Create embedder with mocks
        embedder = Siglip2QBEmbedder(
            model=mock_model,
            processor=mock_processor,
            logger=real_logger
        )

        # Test document
        test_doc = "This is a test question"

        # Call the method
        result = embedder._encode_text(test_doc)

        # Verify the processor was called with correct parameters
        mock_processor.assert_called_once()
        call_args, call_kwargs = mock_processor.call_args
        assert call_kwargs["text"] == test_doc
        assert call_kwargs["images"] is None
        assert call_kwargs["return_tensors"] == "pt"
        assert call_kwargs["padding"] is True

        # Verify the model was called with the processor's output
        mock_model.assert_called_once()

        # Verify the result is the expected tensor
        assert torch.is_tensor(result)
        assert result.shape == expected_shape
        assert torch.equal(result, expected_output)

        real_logger.info("Encode text test completed successfully")


class TestIntegration:
    """Integration tests for QBEmbedder."""

    def test_end_to_end_embedding(self):
        """Test an end-to-end embedding process with a small question bank."""
        pass

    def test_with_real_model(self):
        """Test with a real but small model to ensure proper integration."""
        pass
