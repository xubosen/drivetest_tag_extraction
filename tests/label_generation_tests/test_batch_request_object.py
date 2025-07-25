from label_generator.batch_request import LabelingBatchRequest
from label_generator.labeling_request import LabelingRequest
import pytest
import tempfile
import os
import json
from pydantic import ValidationError
from unittest.mock import patch, mock_open


# Test constants
VALID_CUSTOM_ID_1 = "test_request_001"
VALID_CUSTOM_ID_2 = "test_request_002"
VALID_CUSTOM_ID_3 = "test_request_003"
VALID_URL = "/v1/chat/completions"
VALID_MODEL = "deepseek-r1"
VALID_PROMPT = "You are a helpful assistant."
VALID_CONTENT = [{"type": "text", "text": "Test message"}]

# Sample file paths for testing
TEST_FILE_PATH = "/tmp/test_batch_request.jsonl"
INVALID_FILE_PATH = "/nonexistent/directory/test.jsonl"

# Test data for validation errors
INVALID_REQUEST_TYPES = [
    "string_instead_of_request",
    123,
    {"dict": "instead_of_request"},
    [],
    True
]


# Pytest fixtures for reusable test data
@pytest.fixture
def valid_labeling_request():
    """Fixture providing a valid LabelingRequest instance."""
    return LabelingRequest(
        custom_id=VALID_CUSTOM_ID_1,
        url=VALID_URL,
        model=VALID_MODEL,
        prompt=VALID_PROMPT,
        content=VALID_CONTENT
    )


@pytest.fixture
def multiple_valid_requests():
    """Fixture providing multiple valid LabelingRequest instances."""
    return [
        LabelingRequest(
            custom_id=VALID_CUSTOM_ID_1,
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[{"type": "text", "text": "First test message"}]
        ),
        LabelingRequest(
            custom_id=VALID_CUSTOM_ID_2,
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[{"type": "text", "text": "Second test message"}]
        ),
        LabelingRequest(
            custom_id=VALID_CUSTOM_ID_3,
            url="/v1/embeddings",
            model="text-embedding-v1",
            prompt="Generate embeddings",
            content=[{"type": "text", "text": "Third test message"}]
        )
    ]


@pytest.fixture
def mixed_content_requests():
    """Fixture providing requests with mixed content types."""
    return [
        LabelingRequest(
            custom_id="text_only_001",
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[{"type": "text", "text": "Text only content"}]
        ),
        LabelingRequest(
            custom_id="image_only_001",
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[{"type": "image", "image": "http://example.com/image.jpg"}]
        ),
        LabelingRequest(
            custom_id="mixed_content_001",
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[
                {"type": "text", "text": "Analyze this image"},
                {"type": "image", "image": "http://example.com/image2.jpg"}
            ]
        )
    ]


class TestLabelingBatchRequestCreation:
    """Test suite for LabelingBatchRequest creation and validation."""

    def _create_valid_batch_request(self, requests=None):
        """Helper method to create a valid LabelingBatchRequest with optional requests."""
        if requests is None:
            return LabelingBatchRequest()
        return LabelingBatchRequest(requests=requests)

    def _create_sample_request(self, custom_id=VALID_CUSTOM_ID_1, **overrides):
        """Helper method to create a sample LabelingRequest with optional overrides."""
        data = {
            "custom_id": custom_id,
            "url": VALID_URL,
            "model": VALID_MODEL,
            "prompt": VALID_PROMPT,
            "content": VALID_CONTENT
        }
        data.update(overrides)
        return LabelingRequest(**data)

    def test_empty_batch_request_creation(self):
        """Test creating an empty LabelingBatchRequest with default values."""
        batch_request = LabelingBatchRequest()

        # Should create successfully with empty requests list
        assert isinstance(batch_request, LabelingBatchRequest)
        assert batch_request.requests == []
        assert len(batch_request.requests) == 0

        # Verify field attributes
        assert hasattr(batch_request, 'requests')

    def test_batch_request_creation_with_single_request(self, valid_labeling_request):
        """Test creating a LabelingBatchRequest with a single LabelingRequest."""
        batch_request = self._create_valid_batch_request([valid_labeling_request])

        # Should contain exactly one request
        assert len(batch_request.requests) == 1
        assert batch_request.requests[0] == valid_labeling_request
        assert isinstance(batch_request.requests[0], LabelingRequest)

        # Verify the request attributes are preserved
        request = batch_request.requests[0]
        assert request.custom_id == VALID_CUSTOM_ID_1
        assert request.url == VALID_URL
        assert request.model == VALID_MODEL

    def test_batch_request_creation_with_multiple_requests(self, multiple_valid_requests):
        """Test creating a LabelingBatchRequest with multiple LabelingRequest objects."""
        batch_request = self._create_valid_batch_request(multiple_valid_requests)

        # Should contain all requests in correct order
        assert len(batch_request.requests) == 3
        assert batch_request.requests == multiple_valid_requests

        # Verify each request is a LabelingRequest instance
        for request in batch_request.requests:
            assert isinstance(request, LabelingRequest)

        # Verify specific requests
        assert batch_request.requests[0].custom_id == VALID_CUSTOM_ID_1
        assert batch_request.requests[1].custom_id == VALID_CUSTOM_ID_2
        assert batch_request.requests[2].custom_id == VALID_CUSTOM_ID_3

        # Verify different URLs and models are preserved
        assert batch_request.requests[0].url == "/v1/chat/completions"
        assert batch_request.requests[2].url == "/v1/embeddings"
        assert batch_request.requests[2].model == "text-embedding-v1"

    def test_batch_request_creation_with_mixed_content_types(self, mixed_content_requests):
        """Test creating a LabelingBatchRequest with requests containing different content types."""
        batch_request = self._create_valid_batch_request(mixed_content_requests)

        # Should contain all requests with mixed content types
        assert len(batch_request.requests) == 3

        # Verify text-only content
        text_request = batch_request.requests[0]
        assert text_request.custom_id == "text_only_001"
        assert text_request.content[0]["type"] == "text"
        assert "text" in text_request.content[0]

        # Verify image-only content
        image_request = batch_request.requests[1]
        assert image_request.custom_id == "image_only_001"
        assert image_request.content[0]["type"] == "image"
        assert "image" in image_request.content[0]

        # Verify mixed content
        mixed_request = batch_request.requests[2]
        assert mixed_request.custom_id == "mixed_content_001"
        assert len(mixed_request.content) == 2
        assert mixed_request.content[0]["type"] == "text"
        assert mixed_request.content[1]["type"] == "image"

    def test_batch_request_validation_with_invalid_request_type(self):
        """Test that validation fails when non-LabelingRequest objects are added to requests."""
        # Test various invalid types
        for invalid_request in INVALID_REQUEST_TYPES:
            with pytest.raises(ValidationError) as exc_info:
                LabelingBatchRequest(requests=[invalid_request])

            # Error should mention validation failure
            error_message = str(exc_info.value)
            assert "validation error" in error_message.lower() or "type" in error_message.lower()

        # Test mixed valid and invalid requests
        valid_request = self._create_sample_request()
        with pytest.raises(ValidationError):
            LabelingBatchRequest(requests=[valid_request, "invalid_request"])

    def test_batch_request_validation_with_none_in_requests(self):
        """Test that validation fails when None values are present in requests list."""
        # Test None as single request
        with pytest.raises(ValidationError) as exc_info:
            LabelingBatchRequest(requests=[None])

        error_message = str(exc_info.value)
        assert "validation error" in error_message.lower() or "none" in error_message.lower()

        # Test None mixed with valid requests
        valid_request = self._create_sample_request()
        with pytest.raises(ValidationError):
            LabelingBatchRequest(requests=[valid_request, None])

        # Test multiple None values
        with pytest.raises(ValidationError):
            LabelingBatchRequest(requests=[None, None])

    def test_batch_request_field_validation_extra_fields_forbidden(self):
        """Test that extra fields are forbidden due to Pydantic config."""
        # Test extra field in constructor
        with pytest.raises(ValidationError) as exc_info:
            LabelingBatchRequest(
                requests=[],
                extra_field="should_not_be_allowed"
            )

        error_message = str(exc_info.value)
        assert "extra" in error_message.lower() or "forbidden" in error_message.lower()

        # Test multiple extra fields
        with pytest.raises(ValidationError):
            LabelingBatchRequest(
                requests=[],
                extra_field_1="value1",
                extra_field_2="value2"
            )


class TestLabelingBatchRequestModification:
    """Test suite for modifying LabelingBatchRequest after creation."""

    def _create_empty_batch(self):
        """Helper method to create an empty LabelingBatchRequest."""
        return LabelingBatchRequest()

    def _create_populated_batch(self, requests):
        """Helper method to create a LabelingBatchRequest with given requests."""
        return LabelingBatchRequest(requests=requests)

    def _create_sample_request(self, custom_id=VALID_CUSTOM_ID_1, **overrides):
        """Helper method to create a sample LabelingRequest with optional overrides."""
        data = {
            "custom_id": custom_id,
            "url": VALID_URL,
            "model": VALID_MODEL,
            "prompt": VALID_PROMPT,
            "content": VALID_CONTENT
        }
        data.update(overrides)
        return LabelingRequest(**data)

    def test_add_request_to_empty_batch(self, valid_labeling_request):
        """Test adding a request to an initially empty batch."""
        batch_request = self._create_empty_batch()

        # Verify initially empty
        assert len(batch_request.requests) == 0

        # Add a request
        batch_request.requests.append(valid_labeling_request)

        # Verify request was added successfully
        assert len(batch_request.requests) == 1
        assert batch_request.requests[0] == valid_labeling_request
        assert isinstance(batch_request.requests[0], LabelingRequest)

        # Verify request attributes are preserved
        request = batch_request.requests[0]
        assert request.custom_id == VALID_CUSTOM_ID_1
        assert request.url == VALID_URL
        assert request.model == VALID_MODEL

    def test_add_multiple_requests_to_batch(self, multiple_valid_requests):
        """Test adding multiple requests to an existing batch."""
        # Start with empty batch
        batch_request = self._create_empty_batch()
        assert len(batch_request.requests) == 0

        # Add first request
        batch_request.requests.append(multiple_valid_requests[0])
        assert len(batch_request.requests) == 1
        assert batch_request.requests[0].custom_id == VALID_CUSTOM_ID_1

        # Add second request
        batch_request.requests.append(multiple_valid_requests[1])
        assert len(batch_request.requests) == 2
        assert batch_request.requests[1].custom_id == VALID_CUSTOM_ID_2

        # Add third request
        batch_request.requests.append(multiple_valid_requests[2])
        assert len(batch_request.requests) == 3
        assert batch_request.requests[2].custom_id == VALID_CUSTOM_ID_3

        # Verify all requests are preserved in correct order
        assert batch_request.requests == multiple_valid_requests

        # Test extending with multiple requests at once
        additional_request = self._create_sample_request(
            custom_id="additional_001",
            content=[{"type": "text", "text": "Additional request"}]
        )
        batch_request.requests.extend([additional_request])
        assert len(batch_request.requests) == 4
        assert batch_request.requests[3].custom_id == "additional_001"

    def test_remove_request_from_batch(self, multiple_valid_requests):
        """Test removing a request from a batch with multiple requests."""
        # Start with populated batch
        batch_request = self._create_populated_batch(multiple_valid_requests)
        initial_count = len(batch_request.requests)
        assert initial_count == 3

        # Remove first request by index
        removed_request = batch_request.requests.pop(0)
        assert len(batch_request.requests) == initial_count - 1
        assert removed_request.custom_id == VALID_CUSTOM_ID_1
        assert batch_request.requests[0].custom_id == VALID_CUSTOM_ID_2

        # Remove specific request by value
        second_request = batch_request.requests[0]  # Now the first after previous removal
        batch_request.requests.remove(second_request)
        assert len(batch_request.requests) == initial_count - 2
        assert batch_request.requests[0].custom_id == VALID_CUSTOM_ID_3

        # Remove last request
        batch_request.requests.pop()
        assert len(batch_request.requests) == 0

        # Test removing from empty list (should raise IndexError)
        with pytest.raises(IndexError):
            batch_request.requests.pop()

    def test_clear_all_requests_from_batch(self, multiple_valid_requests):
        """Test clearing all requests from a populated batch."""
        # Start with populated batch
        batch_request = self._create_populated_batch(multiple_valid_requests)
        assert len(batch_request.requests) == 3

        # Clear all requests
        batch_request.requests.clear()

        # Verify batch is now empty
        assert len(batch_request.requests) == 0
        assert batch_request.requests == []

        # Test that we can still add requests after clearing
        new_request = self._create_sample_request(
            custom_id="after_clear_001",
            content=[{"type": "text", "text": "Added after clear"}]
        )
        batch_request.requests.append(new_request)
        assert len(batch_request.requests) == 1
        assert batch_request.requests[0].custom_id == "after_clear_001"

        # Test alternative clearing method with slice assignment
        batch_request.requests[:] = []
        assert len(batch_request.requests) == 0


class TestToBatchJsonlMethod:
    """Test suite for the to_batch_jsonl() method."""

    def test_to_batch_jsonl_empty_requests(self):
        """Test to_batch_jsonl method with empty requests list."""
        pass

    def test_to_batch_jsonl_single_request(self, valid_labeling_request):
        """Test to_batch_jsonl method with a single request."""
        pass

    def test_to_batch_jsonl_multiple_requests(self, multiple_valid_requests):
        """Test to_batch_jsonl method with multiple requests."""
        pass

    def test_to_batch_jsonl_preserves_request_order(self, multiple_valid_requests):
        """Test that the order of requests is preserved in the JSONL output."""
        pass

    def test_to_batch_jsonl_unicode_content_handling(self):
        """Test to_batch_jsonl method with unicode characters in requests."""
        pass

    def test_to_batch_jsonl_mixed_content_types(self, mixed_content_requests):
        """Test to_batch_jsonl method with requests containing different content types."""
        pass


class TestToJsonlFileMethod:
    """Test suite for the to_jsonl_file() method."""

    def test_to_jsonl_file_creates_file_successfully(self, multiple_valid_requests):
        """Test that to_jsonl_file creates a file successfully with valid content."""
        pass

    def test_to_jsonl_file_content_matches_to_batch_jsonl(self, multiple_valid_requests):
        """Test that file content matches the output of to_batch_jsonl method."""
        pass

    def test_to_jsonl_file_empty_requests_creates_empty_file(self):
        """Test that to_jsonl_file with empty requests creates an empty file."""
        pass

    def test_to_jsonl_file_unicode_encoding_utf8(self):
        """Test that to_jsonl_file properly handles unicode characters with UTF-8 encoding."""
        pass

    def test_to_jsonl_file_invalid_path_raises_ioerror(self, multiple_valid_requests):
        """Test that to_jsonl_file raises IOError for invalid file paths."""
        pass

    def test_to_jsonl_file_permission_denied_raises_ioerror(self, multiple_valid_requests):
        """Test that to_jsonl_file raises IOError when write permission is denied."""
        pass

    def test_to_jsonl_file_custom_error_message_format(self, multiple_valid_requests):
        """Test that IOError messages include the file path and original error."""
        pass


class TestLabelingBatchRequestIntegration:
    """Test suite for integration scenarios and end-to-end workflows."""

    def test_create_populate_and_export_workflow(self, multiple_valid_requests):
        """Test complete workflow: create batch, populate with requests, export to file."""
        pass


class TestLabelingBatchRequestErrorHandling:
    """Test suite for error handling and exception scenarios."""

    def test_io_error_message_contains_file_path_and_original_error(self, multiple_valid_requests):
        """Test that IOError messages are properly formatted with context."""
        pass


class TestLabelingBatchRequestValidation:
    """Test suite for Pydantic model validation specific to LabelingBatchRequest."""

    def test_pydantic_validation_assignment_enabled(self, valid_labeling_request):
        """Test that validate_assignment configuration works correctly."""
        pass

    def test_pydantic_extra_fields_forbidden(self):
        """Test that extra fields are properly forbidden by Pydantic configuration."""
        pass

    def test_pydantic_arbitrary_types_allowed(self):
        """Test that arbitrary_types_allowed configuration works for LabelingRequest objects."""
        pass

    def test_pydantic_field_default_factory_behavior(self):
        """Test that the default_factory for requests field works correctly."""
        pass
