from label_generator.labeling_request import LabelingRequest
import pytest
from pydantic import ValidationError


# Test constants
VALID_CUSTOM_ID = "test_request_001"
VALID_URL = "/v1/chat/completions"
VALID_MODEL = "deepseek-r1"
VALID_PROMPT = "You are a helpful assistant."
VALID_CONTENT = [{"type": "text", "text": "Test message"}]

# URL validation constants
VALID_URLS = ["/v1/chat/completions", "/v1/chat/ds-test", "/v1/embeddings"]
INVALID_URLS = ["/v1/invalid", "/v2/chat/completions", "", "not-a-url", "/v1/chat"]

# Model mappings for URL compatibility
URL_MODEL_MAPPING = {
    "/v1/chat/completions": "deepseek-r1",
    "/v1/chat/ds-test": "batch-test-model",
    "/v1/embeddings": "text-embedding-v1"
}

# JSON structure constants for method tests
EXPECTED_JSON_FIELDS = ["custom_id", "method", "url", "body"]
EXPECTED_BODY_FIELDS = ["model", "messages"]
EXPECTED_METHOD_VALUE = "POST"

# Test data constants for edge cases and special characters
SPECIAL_CHARACTERS = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
UNICODE_TEST_DATA = {
    "chinese": "你好世界",
    "japanese": "こんにちは",
    "emoji": "🌟🚀✨💡",
    "french": "Bonjour ça va",
    "mixed": "Hello 世界 🌍 Testing émojis 🎉"
}


# Pytest fixtures for reusable test data
@pytest.fixture
def valid_request_data():
    """Fixture providing valid data for creating a LabelingRequest."""
    return {
        "custom_id": VALID_CUSTOM_ID,
        "url": VALID_URL,
        "model": VALID_MODEL,
        "prompt": VALID_PROMPT,
        "content": VALID_CONTENT
    }


class TestLabelingRequestValidation:
    """Test suite for LabelingRequest field and model validation."""

    def _create_valid_request(self, **overrides):
        """Helper method to create a valid LabelingRequest with optional field overrides."""
        data = {
            "custom_id": VALID_CUSTOM_ID,
            "url": VALID_URL,
            "model": VALID_MODEL,
            "prompt": VALID_PROMPT,
            "content": VALID_CONTENT
        }
        data.update(overrides)
        return LabelingRequest(**data)

    def test_valid_labeling_request_creation(self, valid_request_data):
        """Test creating a valid LabelingRequest with all required fields."""
        request = LabelingRequest(**valid_request_data)

        assert request.custom_id == VALID_CUSTOM_ID
        assert request.url == VALID_URL
        assert request.model == VALID_MODEL
        assert request.prompt == VALID_PROMPT
        assert request.content == VALID_CONTENT
        assert request._method == "POST"

    def test_custom_id_validation_success(self):
        """Test that valid custom_id values are accepted."""
        valid_ids = ["test_001", "request-123", "batch_request_2024", "a" * 100]

        for custom_id in valid_ids:
            request = self._create_valid_request(custom_id=custom_id)
            assert request.custom_id == custom_id

    def test_custom_id_validation_none_fails(self):
        """Test that None custom_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            self._create_valid_request(custom_id=None)

        assert "custom_id" in str(exc_info.value)


class TestUrlValidation:
    """Test suite for URL field validation."""

    def _create_request_with_url(self, url, model=None):
        """Helper method to create a request with a specific URL and compatible model."""
        if model is None:
            model = URL_MODEL_MAPPING.get(url, VALID_MODEL)

        return LabelingRequest(
            custom_id=VALID_CUSTOM_ID,
            url=url,
            model=model,
            prompt=VALID_PROMPT,
            content=VALID_CONTENT
        )

    def test_valid_url_chat_completions(self):
        """Test that /v1/chat/completions URL is accepted."""
        request = self._create_request_with_url("/v1/chat/completions")
        assert request.url == "/v1/chat/completions"

    def test_valid_url_chat_ds_test(self):
        """Test that /v1/chat/ds-test URL is accepted."""
        request = self._create_request_with_url("/v1/chat/ds-test")
        assert request.url == "/v1/chat/ds-test"

    def test_valid_url_embeddings(self):
        """Test that /v1/embeddings URL is accepted."""
        request = self._create_request_with_url("/v1/embeddings",
                                                model="text-embedding-v1")
        assert request.url == "/v1/embeddings"

    def test_invalid_url_raises_value_error(self):
        """Test that invalid URL raises ValueError with appropriate message."""
        for invalid_url in INVALID_URLS:
            with pytest.raises(ValidationError) as exc_info:
                self._create_request_with_url(invalid_url)

            # Check that the error is related to URL validation
            error_message = str(exc_info.value)
            assert "URL must be one of" in error_message or "url" in error_message.lower()


class TestModelValidation:
    """Test suite for model field validation."""

    def test_invalid_model_for_url_raises_value_error(self):
        """Test that model not matching URL raises ValueError."""
        for url, model in URL_MODEL_MAPPING.items():
            if model == "deepseek-r1":
                invalid_model = "invalid-model"
            else:
                invalid_model = "deepseek-r1"

            with pytest.raises(ValidationError) as exc_info:
                LabelingRequest(
                    custom_id=VALID_CUSTOM_ID,
                    url=url,
                    model=invalid_model,
                    prompt=VALID_PROMPT,
                    content=VALID_CONTENT
                )

            assert "model" in str(exc_info.value)


class TestPromptValidation:
    """Test suite for prompt field validation."""

    def test_valid_prompt_accepted(self):
        """Test that valid non-empty prompt is accepted."""
        request = LabelingRequest(
            custom_id=VALID_CUSTOM_ID,
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=VALID_CONTENT
        )
        assert request.prompt == VALID_PROMPT


class TestContentValidation:
    """Test suite for content field validation."""

    def test_valid_text_content_single_item(self):
        """Test that valid single text content item is accepted."""
        request = LabelingRequest(
            custom_id=VALID_CUSTOM_ID,
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[{"type": "text", "text": "Single text item"}]
        )
        assert request.content == [{"type": "text", "text": "Single text item"}]

    def test_valid_text_content_multiple_items(self):
        """Test that valid multiple text content items are accepted."""
        request = LabelingRequest(
            custom_id=VALID_CUSTOM_ID,
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[
                {"type": "text", "text": "First text item"},
                {"type": "text", "text": "Second text item"}
            ]
        )
        assert request.content == [
            {"type": "text", "text": "First text item"},
            {"type": "text", "text": "Second text item"}
        ]

    def test_valid_image_content_single_item(self):
        """Test that valid single image content item is accepted."""
        request = LabelingRequest(
            custom_id=VALID_CUSTOM_ID,
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[{"type": "image", "image": "http://example.com/image.png"}]
        )
        assert request.content == [{"type": "image", "image": "http://example.com/image.png"}]

    def test_valid_mixed_content_text_and_image(self):
        """Test that valid mixed text and image content is accepted."""
        request = LabelingRequest(
            custom_id=VALID_CUSTOM_ID,
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[
                {"type": "text", "text": "Text item"},
                {"type": "image", "image": "http://example.com/image.png"}
            ]
        )
        assert request.content == [
            {"type": "text", "text": "Text item"},
            {"type": "image", "image": "http://example.com/image.png"}
        ]

    def test_content_item_without_type_key_raises_value_error(self):
        """Test that content item missing 'type' key raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            LabelingRequest(
                custom_id=VALID_CUSTOM_ID,
                url=VALID_URL,
                model=VALID_MODEL,
                prompt=VALID_PROMPT,
                content=[{"text": "Missing type key"}]
            )

        assert "type" in str(exc_info.value)

    def test_content_item_with_invalid_type_raises_value_error(self):
        """Test that content item with invalid type raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            LabelingRequest(
                custom_id=VALID_CUSTOM_ID,
                url=VALID_URL,
                model=VALID_MODEL,
                prompt=VALID_PROMPT,
                content=[{"type": "invalid", "text": "Invalid type"}]
            )

        assert "type" in str(exc_info.value)

    def test_content_item_with_wrong_number_of_keys_raises_value_error(self):
        """Test that content item with != 2 keys raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            LabelingRequest(
                custom_id=VALID_CUSTOM_ID,
                url=VALID_URL,
                model=VALID_MODEL,
                prompt=VALID_PROMPT,
                content=[{"type": "text"}]
            )

        assert "content" in str(exc_info.value)

    def test_text_content_without_text_key_raises_value_error(self):
        """Test that text content without 'text' key raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            LabelingRequest(
                custom_id=VALID_CUSTOM_ID,
                url=VALID_URL,
                model=VALID_MODEL,
                prompt=VALID_PROMPT,
                content=[{"type": "text", "image": "image_url"}]
            )

        assert "text" in str(exc_info.value)

    def test_image_content_without_image_key_raises_value_error(self):
        """Test that image content without 'image' key raises ValueError."""
        with pytest.raises(ValidationError) as exc_info:
            LabelingRequest(
                custom_id=VALID_CUSTOM_ID,
                url=VALID_URL,
                model=VALID_MODEL,
                prompt=VALID_PROMPT,
                content=[{"type": "image", "text": "Some text"}]
            )

        assert "image" in str(exc_info.value)


class TestModelUrlCompatibility:
    """Test suite for model-URL compatibility validation."""

    def _create_request_with_model_url(self, url, model):
        """Helper method to create a request with specific model and URL."""
        return LabelingRequest(
            custom_id=VALID_CUSTOM_ID,
            url=url,
            model=model,
            prompt=VALID_PROMPT,
            content=VALID_CONTENT
        )

    def test_deepseek_models_compatible_with_chat_completions(self):
        """Test that all deepseek models are compatible with /v1/chat/completions."""
        deepseek_models = ["deepseek-r1", "deepseek-v3"]

        for model in deepseek_models:
            request = self._create_request_with_model_url("/v1/chat/completions", model)
            assert request.model == model
            assert request.url == "/v1/chat/completions"

    def test_qwen_models_compatible_with_chat_completions(self):
        """Test that all qwen models are compatible with /v1/chat/completions."""
        qwen_models = ["qwen-max", "qwen-plus", "qwen-turbo", "qwen-vl-max"]

        for model in qwen_models:
            request = self._create_request_with_model_url("/v1/chat/completions", model)
            assert request.model == model
            assert request.url == "/v1/chat/completions"

    def test_batch_test_model_compatible_with_ds_test(self):
        """Test that batch-test-model is compatible with /v1/chat/ds-test."""
        request = self._create_request_with_model_url("/v1/chat/ds-test", "batch-test-model")
        assert request.model == "batch-test-model"
        assert request.url == "/v1/chat/ds-test"

    def test_embedding_models_compatible_with_embeddings_url(self):
        """Test that text-embedding models are compatible with /v1/embeddings."""
        embedding_models = ["text-embedding-v1", "text-embedding-v2", "text-embedding-v3", "text-embedding-v4"]

        for model in embedding_models:
            request = self._create_request_with_model_url("/v1/embeddings", model)
            assert request.model == model
            assert request.url == "/v1/embeddings"

    def test_chat_model_incompatible_with_embeddings_url(self):
        """Test that chat models are incompatible with /v1/embeddings URL."""
        chat_models = ["deepseek-r1", "qwen-max", "batch-test-model"]

        for model in chat_models:
            with pytest.raises(ValidationError) as exc_info:
                self._create_request_with_model_url("/v1/embeddings", model)

            error_message = str(exc_info.value)
            assert "not valid for URL" in error_message

    def test_embedding_model_incompatible_with_chat_url(self):
        """Test that embedding models are incompatible with chat URLs."""
        embedding_models = ["text-embedding-v1", "text-embedding-v2"]
        chat_urls = ["/v1/chat/completions", "/v1/chat/ds-test"]

        for model in embedding_models:
            for url in chat_urls:
                with pytest.raises(ValidationError) as exc_info:
                    self._create_request_with_model_url(url, model)

                error_message = str(exc_info.value)
                assert "not valid for URL" in error_message


class TestLabelingRequestMethods:
    """Test suite for LabelingRequest methods."""

    def _create_test_request(self, **overrides):
        """Helper method to create a LabelingRequest for method testing."""
        data = {
            "custom_id": VALID_CUSTOM_ID,
            "url": VALID_URL,
            "model": VALID_MODEL,
            "prompt": VALID_PROMPT,
            "content": VALID_CONTENT
        }
        data.update(overrides)
        return LabelingRequest(**data)

    def _parse_json_output(self, request):
        """Helper method to parse JSON output from to_request method."""
        import json
        json_string = request.to_request()
        return json.loads(json_string)

    def test_to_request_method_returns_valid_jsonl(self):
        """Test that to_request method returns valid JSONL format."""
        request = self._create_test_request()
        json_output = request.to_request()

        # Should return a string
        assert isinstance(json_output, str)

        # Should be valid JSON (no parsing errors)
        import json
        parsed = json.loads(json_output)
        assert isinstance(parsed, dict)

    def test_to_request_includes_all_required_fields(self):
        """Test that to_request includes custom_id, method, url, and body."""
        request = self._create_test_request()
        parsed_output = self._parse_json_output(request)

        # Check all expected top-level fields are present
        for field in EXPECTED_JSON_FIELDS:
            assert field in parsed_output, f"Missing required field: {field}"

        # Verify specific values
        assert parsed_output["custom_id"] == VALID_CUSTOM_ID
        assert parsed_output["method"] == EXPECTED_METHOD_VALUE
        assert parsed_output["url"] == VALID_URL
        assert isinstance(parsed_output["body"], dict)

    def test_to_request_body_structure_correct(self):
        """Test that body contains model and messages with correct structure."""
        request = self._create_test_request()
        parsed_output = self._parse_json_output(request)

        body = parsed_output["body"]

        # Check body has required fields
        for field in EXPECTED_BODY_FIELDS:
            assert field in body, f"Missing body field: {field}"

        # Verify body field values
        assert body["model"] == VALID_MODEL
        assert isinstance(body["messages"], list)
        assert len(body["messages"]) == 2  # system + user messages

    def test_to_request_messages_structure_system_and_user(self):
        """Test that messages array has system and user roles correctly."""
        request = self._create_test_request()
        parsed_output = self._parse_json_output(request)

        messages = parsed_output["body"]["messages"]

        # Check message structure
        assert len(messages) == 2

        # System message (first)
        system_msg = messages[0]
        assert system_msg["role"] == "system"
        assert system_msg["content"] == VALID_PROMPT

        # User message (second)
        user_msg = messages[1]
        assert user_msg["role"] == "user"
        assert user_msg["content"] == VALID_CONTENT

    def test_to_request_with_unicode_characters(self):
        """Test that to_request handles unicode characters correctly."""
        unicode_data = {
            "custom_id": "测试_001",  # Chinese characters
            "prompt": "Bonjour! Comment ça va? 你好！🌟",  # French + Chinese + emoji
            "content": [{"type": "text", "text": "测试内容 with émojis 🚀✨"}]
        }

        request = self._create_test_request(**unicode_data)
        json_output = request.to_request()
        parsed_output = self._parse_json_output(request)

        # Verify unicode characters are preserved
        assert parsed_output["custom_id"] == unicode_data["custom_id"]
        assert parsed_output["body"]["messages"][0]["content"] == unicode_data["prompt"]
        assert parsed_output["body"]["messages"][1]["content"] == unicode_data["content"]

        # Verify the string contains unicode characters (not escaped)
        assert "测试" in json_output
        assert "🌟" in json_output


class TestLabelingRequestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_special_characters_in_fields(self):
        """Test handling of special characters in various fields."""
        request = LabelingRequest(
            custom_id=VALID_CUSTOM_ID,
            url=VALID_URL,
            model=VALID_MODEL,
            prompt=VALID_PROMPT,
            content=[
                {"type": "text", "text": "Normal text"},
                {"type": "text", "text": SPECIAL_CHARACTERS},
                {"type": "text", "text": UNICODE_TEST_DATA["chinese"]},
                {"type": "text", "text": UNICODE_TEST_DATA["japanese"]},
                {"type": "text", "text": UNICODE_TEST_DATA["emoji"]},
                {"type": "text", "text": UNICODE_TEST_DATA["french"]},
                {"type": "text", "text": UNICODE_TEST_DATA["mixed"]},
            ]
        )

        assert request.content[0]["text"] == "Normal text"
        assert request.content[1]["text"] == SPECIAL_CHARACTERS
        assert request.content[2]["text"] == UNICODE_TEST_DATA["chinese"]
        assert request.content[3]["text"] == UNICODE_TEST_DATA["japanese"]
        assert request.content[4]["text"] == UNICODE_TEST_DATA["emoji"]
        assert request.content[5]["text"] == UNICODE_TEST_DATA["french"]
        assert request.content[6]["text"] == UNICODE_TEST_DATA["mixed"]


class TestLabelingRequestSerialization:
    """Test suite for JSON serialization and deserialization."""

    def _create_test_request(self, **overrides):
        """Helper method to create a LabelingRequest for serialization testing."""
        data = {
            "custom_id": VALID_CUSTOM_ID,
            "url": VALID_URL,
            "model": VALID_MODEL,
            "prompt": VALID_PROMPT,
            "content": VALID_CONTENT
        }
        data.update(overrides)
        return LabelingRequest(**data)

    def test_json_output_is_valid_json(self):
        """Test that to_request output is valid JSON that can be parsed."""
        request = self._create_test_request()
        json_output = request.to_request()

        # Should be valid JSON that can be parsed
        import json
        try:
            parsed_json = json.loads(json_output)
            assert isinstance(parsed_json, dict)
        except json.JSONDecodeError:
            pytest.fail("to_request output is not valid JSON")

        # Should contain expected structure
        assert "custom_id" in parsed_json
        assert "method" in parsed_json
        assert "url" in parsed_json
        assert "body" in parsed_json

        # Verify round-trip consistency
        second_output = request.to_request()
        assert json_output == second_output  # Should be deterministic


class TestLabelingRequestIntegration:
    """Test suite for integration scenarios."""

    def _create_sample_requests(self):
        """Helper method to create multiple sample requests for integration testing."""
        requests = []

        # Chat completion request
        requests.append(LabelingRequest(
            custom_id="chat_001",
            url="/v1/chat/completions",
            model="deepseek-r1",
            prompt="You are a helpful assistant for image analysis.",
            content=[{"type": "text", "text": "Analyze this image for safety concerns."}]
        ))

        # Embedding request
        requests.append(LabelingRequest(
            custom_id="embed_001",
            url="/v1/embeddings",
            model="text-embedding-v1",
            prompt="Generate embeddings for this text.",
            content=[{"type": "text", "text": "Sample text for embedding generation."}]
        ))

        # DS test request
        requests.append(LabelingRequest(
            custom_id="test_001",
            url="/v1/chat/ds-test",
            model="batch-test-model",
            prompt="Test prompt for batch processing.",
            content=[{"type": "text", "text": "Test content for validation."}]
        ))

        return requests

    def test_request_creation_workflow_end_to_end(self):
        """Test complete workflow from creation to JSON output."""
        # Step 1: Create request with valid data
        request_data = {
            "custom_id": "workflow_test_001",
            "url": "/v1/chat/completions",
            "model": "qwen-max",
            "prompt": "You are an AI assistant that analyzes images for content moderation.",
            "content": [
                {"type": "text", "text": "Please analyze this image"},
                {"type": "image", "image": "https://example.com/test_image.jpg"}
            ]
        }

        # Step 2: Create LabelingRequest instance
        request = LabelingRequest(**request_data)

        # Step 3: Verify all fields are correctly set
        assert request.custom_id == request_data["custom_id"]
        assert request.url == request_data["url"]
        assert request.model == request_data["model"]
        assert request.prompt == request_data["prompt"]
        assert request.content == request_data["content"]
        assert request._method == "POST"

        # Step 4: Generate JSON output
        json_output = request.to_request()

        # Step 5: Verify JSON is valid and has correct structure
        import json
        parsed_output = json.loads(json_output)

        # Verify top-level structure
        assert parsed_output["custom_id"] == request_data["custom_id"]
        assert parsed_output["method"] == "POST"
        assert parsed_output["url"] == request_data["url"]

        # Verify body structure
        body = parsed_output["body"]
        assert body["model"] == request_data["model"]
        assert len(body["messages"]) == 2
        assert body["messages"][0]["role"] == "system"
        assert body["messages"][0]["content"] == request_data["prompt"]
        assert body["messages"][1]["role"] == "user"
        assert body["messages"][1]["content"] == request_data["content"]

        # Step 6: Verify __str__ method works
        str_output = str(request)
        assert str_output == json_output

        # Step 7: Test with multiple requests (batch scenario)
        requests = self._create_sample_requests()
        json_outputs = []

        for req in requests:
            json_line = req.to_request()
            json_outputs.append(json_line)

            # Each should be valid JSON
            parsed = json.loads(json_line)
            assert isinstance(parsed, dict)
            assert all(field in parsed for field in EXPECTED_JSON_FIELDS)

        # All outputs should be different (different custom_ids)
        assert len(set(json_outputs)) == len(json_outputs)
