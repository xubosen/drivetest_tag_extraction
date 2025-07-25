from label_generator.batch_request import LabelingBatchRequest
from label_generator.labeling_request import LabelingRequest
import pytest
import tempfile
import os
import json
from pydantic import ValidationError


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
READONLY_FILE_PATH = "/tmp/readonly_test_batch_request.jsonl"

# Test data for validation errors
INVALID_REQUEST_TYPES = [
    "string_instead_of_request",
    123,
    {"dict": "instead_of_request"},
    [],
    True
]

# Additional test constants for file operations
TEMP_FILE_PREFIX = "test_batch_request_"
TEMP_FILE_SUFFIX = ".jsonl"

# Unicode test constants
UNICODE_CHARACTERS = {
    "chinese": "你好世界",
    "japanese": "こんにちは世界",
    "emoji": "🌟🚀✨💡",
    "french": "Bonjour ça va très bien",
    "mixed": "Hello 世界 🌍 Testing émojis 🎉",
    "special_chars": "!@#$%^&*()_+-=[]{}|;':,./<>?"
}


# Helper functions for test setup and cleanup
def create_readonly_file(file_path: str) -> None:
    """Create a read-only file for permission testing."""
    with open(file_path, 'w') as f:
        f.write("test content")
    os.chmod(file_path, 0o444)  # Read-only permissions


def cleanup_test_file(file_path: str) -> None:
    """Clean up test files with proper error handling."""
    try:
        if os.path.exists(file_path):
            # Reset permissions if needed
            os.chmod(file_path, 0o644)
            os.remove(file_path)
    except (OSError, PermissionError):
        pass  # Ignore cleanup errors in tests


def create_sample_labeling_request(custom_id: str = VALID_CUSTOM_ID_1, **overrides) -> LabelingRequest:
    """Helper function to create a LabelingRequest with optional overrides."""
    data = {
        "custom_id": custom_id,
        "url": VALID_URL,
        "model": VALID_MODEL,
        "prompt": VALID_PROMPT,
        "content": VALID_CONTENT
    }
    data.update(overrides)
    return LabelingRequest(**data)


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

    def _create_batch_request(self, requests=None):
        """Helper method to create a LabelingBatchRequest with optional requests."""
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

    def _parse_jsonl_lines(self, jsonl_output):
        """Helper method to parse JSONL output into individual JSON objects."""
        if not jsonl_output.strip():
            return []
        return [json.loads(line) for line in jsonl_output.strip().split('\n')]

    def test_to_batch_jsonl_empty_requests(self):
        """Test to_batch_jsonl method with empty requests list."""
        batch_request = self._create_batch_request()
        result = batch_request.to_batch_jsonl()

        # Empty requests should return empty string
        assert result == ""
        assert len(result) == 0

    def test_to_batch_jsonl_single_request(self, valid_labeling_request):
        """Test to_batch_jsonl method with a single request."""
        batch_request = self._create_batch_request([valid_labeling_request])
        result = batch_request.to_batch_jsonl()

        # Should return single line of JSON
        lines = result.strip().split('\n')
        assert len(lines) == 1

        # Parse and verify JSON structure
        parsed_request = json.loads(lines[0])
        assert parsed_request["custom_id"] == VALID_CUSTOM_ID_1
        assert parsed_request["method"] == "POST"
        assert parsed_request["url"] == VALID_URL
        assert "body" in parsed_request

        body = parsed_request["body"]
        assert body["model"] == VALID_MODEL
        assert "messages" in body
        assert len(body["messages"]) == 2
        assert body["messages"][0]["role"] == "system"
        assert body["messages"][0]["content"] == VALID_PROMPT
        assert body["messages"][1]["role"] == "user"
        assert body["messages"][1]["content"] == VALID_CONTENT

    def test_to_batch_jsonl_multiple_requests(self, multiple_valid_requests):
        """Test to_batch_jsonl method with multiple requests."""
        batch_request = self._create_batch_request(multiple_valid_requests)
        result = batch_request.to_batch_jsonl()

        # Should return multiple lines
        lines = result.strip().split('\n')
        assert len(lines) == len(multiple_valid_requests)

        # Verify each line is valid JSON with correct structure
        for i, line in enumerate(lines):
            parsed_request = json.loads(line)
            original_request = multiple_valid_requests[i]

            assert parsed_request["custom_id"] == original_request.custom_id
            assert parsed_request["method"] == "POST"
            assert parsed_request["url"] == original_request.url

            body = parsed_request["body"]
            assert body["model"] == original_request.model
            assert body["messages"][0]["content"] == original_request.prompt
            assert body["messages"][1]["content"] == original_request.content

    def test_to_batch_jsonl_preserves_request_order(self, multiple_valid_requests):
        """Test that the order of requests is preserved in the JSONL output."""
        batch_request = self._create_batch_request(multiple_valid_requests)
        result = batch_request.to_batch_jsonl()

        parsed_lines = self._parse_jsonl_lines(result)
        assert len(parsed_lines) == len(multiple_valid_requests)

        # Verify order is preserved by checking custom_ids
        for i, parsed_request in enumerate(parsed_lines):
            expected_custom_id = multiple_valid_requests[i].custom_id
            assert parsed_request["custom_id"] == expected_custom_id

        # Test with reversed order to ensure order dependency
        reversed_requests = list(reversed(multiple_valid_requests))
        batch_request_reversed = self._create_batch_request(reversed_requests)
        result_reversed = batch_request_reversed.to_batch_jsonl()

        parsed_lines_reversed = self._parse_jsonl_lines(result_reversed)
        for i, parsed_request in enumerate(parsed_lines_reversed):
            expected_custom_id = reversed_requests[i].custom_id
            assert parsed_request["custom_id"] == expected_custom_id

    def test_to_batch_jsonl_unicode_content_handling(self):
        """Test to_batch_jsonl method with unicode characters in requests."""
        unicode_requests = []

        # Create requests with various unicode content
        for key, unicode_text in UNICODE_CHARACTERS.items():
            request = self._create_sample_request(
                custom_id=f"unicode_{key}",
                prompt=f"Process this:",
                content=[{"type": "text", "text": unicode_text}]
            )
            unicode_requests.append(request)

        batch_request = self._create_batch_request(unicode_requests)
        result = batch_request.to_batch_jsonl()

        # Verify all unicode characters are present in output
        for unicode_text in UNICODE_CHARACTERS.values():
            assert unicode_text in result

        # Verify each line is valid JSON
        parsed_lines = self._parse_jsonl_lines(result)
        assert len(parsed_lines) == len(unicode_requests)

        # Verify unicode preservation in parsed JSON
        for i, parsed_request in enumerate(parsed_lines):
            expected_unicode = list(UNICODE_CHARACTERS.values())[i]
            assert expected_unicode in str(parsed_request)

    def test_to_batch_jsonl_mixed_content_types(self, mixed_content_requests):
        """Test to_batch_jsonl method with requests containing different content types."""
        batch_request = self._create_batch_request(mixed_content_requests)
        result = batch_request.to_batch_jsonl()

        parsed_lines = self._parse_jsonl_lines(result)
        assert len(parsed_lines) == len(mixed_content_requests)

        # Verify each request type is correctly represented
        for i, parsed_request in enumerate(parsed_lines):
            original_request = mixed_content_requests[i]

            # Check basic structure
            assert parsed_request["custom_id"] == original_request.custom_id
            assert parsed_request["url"] == original_request.url

            # Check content in the user message
            user_content = parsed_request["body"]["messages"][1]["content"]
            assert user_content == original_request.content

            # Verify content types are preserved
            for content_item in user_content:
                assert content_item["type"] in ["text", "image"]
                if content_item["type"] == "text":
                    assert "text" in content_item
                elif content_item["type"] == "image":
                    assert "image" in content_item


class TestToJsonlFileMethod:
    """Test suite for the to_jsonl_file() method."""

    def test_to_jsonl_file_creates_file_successfully(
            self, multiple_valid_requests):
        """Test that to_jsonl_file creates a file successfully with valid content."""
        batch_request = LabelingBatchRequest(requests=multiple_valid_requests)
        file_path = TEST_FILE_PATH

        # Ensure file does not exist before test
        if os.path.exists(file_path):
            os.remove(file_path)

        batch_request.to_jsonl_file(file_path)

        # Verify file was created and contains expected content
        assert os.path.exists(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        assert file_content == batch_request.to_batch_jsonl()

        # Clean up test file
        os.remove(file_path)

    def test_to_jsonl_file_content_matches_to_batch_jsonl(
            self, multiple_valid_requests):
        """Test that file content matches the output of to_batch_jsonl method."""
        batch_request = LabelingBatchRequest(requests=multiple_valid_requests)
        file_path = TEST_FILE_PATH

        # Ensure file does not exist before test
        if os.path.exists(file_path):
            os.remove(file_path)

        batch_request.to_jsonl_file(file_path)

        # Read back the file content
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        assert file_content == batch_request.to_batch_jsonl()

        # Clean up test file
        os.remove(file_path)

    def test_to_jsonl_file_empty_requests_creates_empty_file(self):
        """Test that to_jsonl_file with empty requests creates an empty file."""
        batch_request = LabelingBatchRequest(requests=[])
        file_path = TEST_FILE_PATH

        # Ensure file does not exist before test
        if os.path.exists(file_path):
            os.remove(file_path)

        batch_request.to_jsonl_file(file_path)

        # Verify file was created and is empty
        assert os.path.exists(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        assert file_content == ""

        # Clean up test file
        os.remove(file_path)

    def test_to_jsonl_file_unicode_encoding_utf8(self):
        """Test that to_jsonl_file properly handles unicode characters with UTF-8 encoding."""
        unicode_request = LabelingRequest(
            custom_id="unicode_test",
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[
                {"type": "text", "text": UNICODE_CHARACTERS["chinese"]},
                {"type": "text", "text": UNICODE_CHARACTERS["japanese"]},
                {"type": "text", "text": UNICODE_CHARACTERS["emoji"]},
                {"type": "text", "text": UNICODE_CHARACTERS["french"]},
                {"type": "text", "text": UNICODE_CHARACTERS["mixed"]},
                {"type": "text", "text": UNICODE_CHARACTERS["special_chars"]},
            ]
        )
        batch_request = LabelingBatchRequest(requests=[unicode_request])
        file_path = TEST_FILE_PATH

        # Ensure file does not exist before test
        if os.path.exists(file_path):
            os.remove(file_path)

        batch_request.to_jsonl_file(file_path)

        # Verify file was created and contains the unicode content
        assert os.path.exists(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        # Check that the file content contains the unicode characters
        for value in UNICODE_CHARACTERS.values():
            assert value in file_content

        # Clean up test file
        os.remove(file_path)

    def test_to_jsonl_file_invalid_path(self, multiple_valid_requests):
        """Test that to_jsonl_file raises OSError for invalid file paths."""
        batch_request = LabelingBatchRequest(requests=multiple_valid_requests)
        with pytest.raises(OSError) as exc_info:
            batch_request.to_jsonl_file(INVALID_FILE_PATH)
        assert INVALID_FILE_PATH in str(exc_info.value)

    def test_to_jsonl_file_permission_denied(self):
        """Test that to_jsonl_file raises OSError when write permission is denied."""
        # Create a test batch request
        sample_request = create_sample_labeling_request("perm_test_001")
        batch_request = LabelingBatchRequest(requests=[sample_request])

        # Create a read-only file first (to ensure directory exists)
        readonly_path = READONLY_FILE_PATH
        create_readonly_file(readonly_path)

        try:
            # Attempt to write to the read-only file should raise OSError
            with pytest.raises(OSError) as exc_info:
                batch_request.to_jsonl_file(readonly_path)

            # Verify the error message mentions the file path
            error_message = str(exc_info.value)
            assert readonly_path in error_message or "Permission denied" in error_message

        finally:
            # Clean up the test file
            cleanup_test_file(readonly_path)

    def test_to_jsonl_file_custom_error_message_format(
            self, multiple_valid_requests):
        """Test that error messages include the file path and original
        error."""
        batch_request = LabelingBatchRequest(requests=multiple_valid_requests)
        with pytest.raises(OSError) as exc_info:
            batch_request.to_jsonl_file(INVALID_FILE_PATH)
        assert str(INVALID_FILE_PATH) in str(exc_info.value)


class TestLabelingBatchRequestIntegration:
    """Test suite for integration scenarios and end-to-end workflows."""

    def test_create_populate_and_export_workflow(self, multiple_valid_requests):
        """Test complete workflow: create batch, populate with requests, export to file."""
        # Step 1: Create an empty batch request
        batch_request = LabelingBatchRequest()
        assert len(batch_request.requests) == 0

        # Step 2: Populate with requests one by one
        for request in multiple_valid_requests:
            batch_request.requests.append(request)

        assert len(batch_request.requests) == len(multiple_valid_requests)

        # Step 3: Generate JSONL content
        jsonl_content = batch_request.to_batch_jsonl()
        assert jsonl_content != ""

        # Verify content structure
        lines = jsonl_content.strip().split('\n')
        assert len(lines) == len(multiple_valid_requests)

        for i, line in enumerate(lines):
            parsed = json.loads(line)
            assert parsed["custom_id"] == multiple_valid_requests[i].custom_id
            assert parsed["method"] == "POST"
            assert "body" in parsed

        # Step 4: Export to file using temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=TEMP_FILE_SUFFIX,
                                       prefix=TEMP_FILE_PREFIX, delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Export to file
            batch_request.to_jsonl_file(temp_path)

            # Step 5: Verify file was created and has correct content
            assert os.path.exists(temp_path)

            with open(temp_path, 'r', encoding='utf-8') as f:
                file_content = f.read()

            assert file_content == jsonl_content

            # Step 6: Verify we can parse each line in the file
            file_lines = file_content.strip().split('\n')
            for line in file_lines:
                parsed = json.loads(line)
                assert "custom_id" in parsed
                assert "method" in parsed
                assert "url" in parsed
                assert "body" in parsed

        finally:
            # Clean up
            cleanup_test_file(temp_path)


class TestLabelingBatchRequestValidation:
    """Test suite for Pydantic model validation specific to LabelingBatchRequest."""

    def test_pydantic_validation_assignment_enabled(self, valid_labeling_request):
        """Test that validate_assignment configuration works correctly."""
        # Create a batch request with initial data
        batch_request = LabelingBatchRequest(requests=[valid_labeling_request])
        assert len(batch_request.requests) == 1

        # Test that we can assign valid LabelingRequest objects after creation
        new_request = create_sample_labeling_request("validation_test_001")
        batch_request.requests = [new_request]
        assert len(batch_request.requests) == 1
        assert batch_request.requests[0].custom_id == "validation_test_001"

        # Test that assignment validation catches invalid types
        with pytest.raises(ValidationError) as exc_info:
            batch_request.requests = ["invalid_request"]

        error_message = str(exc_info.value)
        assert "validation error" in error_message.lower() or "type" in error_message.lower()

    def test_pydantic_extra_fields_forbidden(self):
        """Test that extra fields are properly forbidden by Pydantic configuration."""
        # Test that extra fields in constructor are forbidden
        with pytest.raises(ValidationError) as exc_info:
            LabelingBatchRequest(
                requests=[],
                unexpected_field="not_allowed"
            )

        error_message = str(exc_info.value)
        assert "extra" in error_message.lower() or "forbidden" in error_message.lower()

        # Test that setting extra attributes after creation is also forbidden
        batch_request = LabelingBatchRequest()

        # Pydantic should prevent setting extra attributes
        with pytest.raises((ValidationError, AttributeError)):
            batch_request.extra_attribute = "should_fail"

    def test_pydantic_arbitrary_types_allowed(self):
        """Test that arbitrary_types_allowed configuration works for LabelingRequest objects."""
        # Create LabelingRequest objects (which are custom types)
        request1 = create_sample_labeling_request("arbitrary_test_001")
        request2 = create_sample_labeling_request("arbitrary_test_002")

        # Test that custom LabelingRequest objects are accepted
        batch_request = LabelingBatchRequest(requests=[request1, request2])

        assert len(batch_request.requests) == 2
        assert isinstance(batch_request.requests[0], LabelingRequest)
        assert isinstance(batch_request.requests[1], LabelingRequest)
        assert batch_request.requests[0].custom_id == "arbitrary_test_001"
        assert batch_request.requests[1].custom_id == "arbitrary_test_002"

        # Test that other arbitrary types are still rejected
        with pytest.raises(ValidationError):
            LabelingBatchRequest(requests=[request1, object()])

    def test_pydantic_field_default_factory_behavior(self):
        """Test that the default_factory for requests field works correctly."""
        # Test that creating without requests parameter uses default_factory
        batch_request1 = LabelingBatchRequest()
        batch_request2 = LabelingBatchRequest()

        # Both should have empty lists but different instances
        assert batch_request1.requests == []
        assert batch_request2.requests == []
        assert batch_request1.requests is not batch_request2.requests  # Different instances

        # Test that modifying one doesn't affect the other
        sample_request = create_sample_labeling_request("factory_test_001")
        batch_request1.requests.append(sample_request)

        assert len(batch_request1.requests) == 1
        assert len(batch_request2.requests) == 0

        # Test that explicit empty list also works
        batch_request3 = LabelingBatchRequest(requests=[])
        assert batch_request3.requests == []
        assert len(batch_request3.requests) == 0
