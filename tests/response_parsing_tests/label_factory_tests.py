import pytest
from pydantic import ValidationError

from label_generator.label_factory import LabelFactory, MessageFormatConfig
from label_generator.label_data import LabelData
from label_generator.response_object import Message


SAMPLE_QUESTION = \
    ("<THINKING>\n"
     "**第一步：生成推理依据**\n"
     "  * **步骤1：视觉观察与文本提取 (Keywords)**\n"
     "      * **视觉元素**: 图像展示了一个标准的交通标志。其特征包括：一个红色的圆形边框，"
     "一道从左上到右下的红色斜杠，以及白色的背景。标志内部有两个黑色的箭头符号：一个指向上方"
     "（代表直行），另一个从主干道向右弯曲（代表右转）。\n"
     "      * **文本信息**: 问题文本为“这个标志是何含义？”，选项中包含了“禁止直行”、"
     "“向右转弯”等关键术语。\n"
     "      * **关键词**: 交通标志, 禁令标志, 禁止直行, 禁止右转, 红色圆形\n"
     "  * **步骤2：分析与关联**\n"
     "      * **分析**: 红色圆形加红色斜杠的组合是中国交通标志中典型的“禁令标志”形式，"
     "表示禁止或限制。内部的黑色图案则指明了被禁止的具体行为。此标志将“禁止直行”和“禁止右转”"
     "两个指令结合在一起。\n"
     "      * **关联法规**: 该标志考察的是驾驶员对《道路交通安全法》中禁令标志的识别能力，"
     "要求驾驶员在行至设有此标志的路口时，不得直行也不得右转。\n"
     "  * **步骤3：归纳与生成 (Tags)**\n"
     "      * **核心概念**: 此题的核心是考察驾驶员对交通信号的认知，具体到交通标志中的一个"
     "特定类别——禁令标志。\n"
     "      * **标签**: 交通信号-标志-禁令\n"
     "</THINKING>\n"
     "<OUTPUT>\n"
     "**第二步：生成JSON**\n"
     "<JSON>"
     "{"
     "\"keywords\": [\"交通标志\", \"禁令标志\", \"禁止直行\", \"禁止右转\", "
     "\"红色圆形\"], "
     "\"tags\": [\"交通信号-标志-禁令\"]"
     "}"
     "</JSON>\n"
     "</OUTPUT>")
VALID_JSON_CONTENT = ('{"keywords": ["test1", "test2"], '
                      '"tags": ["tag1", "tag2"]}')
EMPTY_JSON_CONTENT = ''
WHITESPACE_JSON_CONTENT = '   {"keywords": [], "tags": []}   '


@pytest.fixture
def sample_valid_message():
    """
    Fixture to create a Message object with sample content.
    """
    return Message(role="assistant", content=SAMPLE_QUESTION)


@pytest.fixture
def default_message_format():
    """
    Fixture to create a default MessageFormatConfig.
    """
    return MessageFormatConfig(output_start_tag="<OUTPUT>",
                               output_end_tag="</OUTPUT>")


@pytest.fixture
def custom_message_format():
    """
    Fixture to create a custom MessageFormatConfig with different tags.
    """
    return MessageFormatConfig(
        output_start_tag="<CUSTOM>",
        output_end_tag="</CUSTOM>"
    )


@pytest.fixture
def default_label_factory(default_message_format):
    """
    Fixture to create a LabelFactory with default configuration.
    """
    my_format = default_message_format
    return LabelFactory(message_format=my_format)


@pytest.fixture
def custom_label_factory(custom_message_format):
    """
    Fixture to create a LabelFactory with custom configuration.
    """
    return LabelFactory(message_format=custom_message_format)


@pytest.fixture
def json_extraction_factory(default_message_format):
    """
    Fixture to create a LabelFactory for JSON extraction testing.
    """
    return LabelFactory(message_format=default_message_format)


@pytest.fixture
def valid_content_with_tags():
    """
    Fixture providing valid message content with proper tags and JSON.
    """
    return f"<OUTPUT>{VALID_JSON_CONTENT}</OUTPUT>"


@pytest.fixture
def content_missing_start_tag():
    """
    Fixture providing content missing the start tag.
    """
    return f"{VALID_JSON_CONTENT}</OUTPUT>"


@pytest.fixture
def content_missing_end_tag():
    """
    Fixture providing content missing the end tag.
    """
    return f"<OUTPUT>{VALID_JSON_CONTENT}"


@pytest.fixture
def content_missing_both_tags():
    """
    Fixture providing content with no tags at all.
    """
    return VALID_JSON_CONTENT


@pytest.fixture
def content_with_multiple_tags():
    """
    Fixture providing content with multiple occurrences of tags.
    """
    return (f"<OUTPUT>first content</OUTPUT>some text<OUTPUT>second content"
            f"</OUTPUT>")


@pytest.fixture
def content_with_empty_tags():
    """
    Fixture providing content with empty space between tags.
    """
    return f"<OUTPUT>{EMPTY_JSON_CONTENT}</OUTPUT>"


@pytest.fixture
def content_with_whitespace():
    """
    Fixture providing content with whitespace around JSON.
    """
    return f"<OUTPUT>{WHITESPACE_JSON_CONTENT}</OUTPUT>"


class TestMessageFormatConfig:
    """
    Test class for MessageFormatConfig validation and configuration.

    This class tests the configuration object that defines how to parse
    message content for extracting JSON data between specific tags.
    """

    def test_default_config_creation(self):
        """
        Test creation of MessageFormatConfig with default values.

        Should create config with default <OUTPUT> and </OUTPUT> tags.
        """
        config = MessageFormatConfig(output_start_tag="<OUTPUT>",
                                     output_end_tag="</OUTPUT>")
        assert config.output_start_tag == "<OUTPUT>"
        assert config.output_end_tag == "</OUTPUT>"

    def test_custom_config_creation(self):
        """
        Test creation of MessageFormatConfig with custom tag values.

        Should allow setting custom start and end tags for output sections.
        """
        config = MessageFormatConfig(
            output_start_tag="<RESULT>",
            output_end_tag="</RESULT>"
        )
        assert config.output_start_tag == "<RESULT>"
        assert config.output_end_tag == "</RESULT>"

    def test_config_validation_empty_tags(self):
        """
        Test that start or end tags cannot be empty.
        """
        # Test empty start tag
        with pytest.raises(ValidationError):
            MessageFormatConfig(output_start_tag="")

        # Test empty end tag
        with pytest.raises(ValidationError):
            MessageFormatConfig(output_end_tag="")

        # Test both empty
        with pytest.raises(ValidationError):
            MessageFormatConfig(output_start_tag="", output_end_tag="")

    def test_config_validation_same_tags(self):
        """
        Test that start and end tags cannot be identical.
        """
        with pytest.raises(ValueError, match="Start and end tags must be "
                                             "different"):
            MessageFormatConfig(
                output_start_tag="<TAG>",
                output_end_tag="<TAG>"
            )

    def test_config_immutability_after_creation(self, default_message_format):
        """
        Test that config fields cannot be modified after creation.
        """
        config = default_message_format

        # Try to modify fields - should raise ValidationError due to frozen=True
        with pytest.raises(ValueError):
            config.output_start_tag = "<NEW_TAG>"

        with pytest.raises(ValueError):
            config.output_end_tag = "</NEW_TAG>"


class TestLabelFactoryInitialization:
    """
    Test class for LabelFactory initialization and configuration.

    This class tests the proper initialization of LabelFactory instances
    with different MessageFormatConfig objects.
    """

    def test_factory_creation_with_default_config(self,
                                                  default_label_factory):
        """
        Test LabelFactory creation with default MessageFormatConfig.
        """
        my_factory = default_label_factory
        assert my_factory._msg_format is not None
        assert my_factory._msg_format.output_start_tag == "<OUTPUT>"
        assert my_factory._msg_format.output_end_tag == "</OUTPUT>"

    def test_factory_creation_with_custom_config(self, custom_label_factory):
        """
        Test LabelFactory creation with custom MessageFormatConfig.

        Should successfully create factory with custom output tags.
        """
        my_factory = custom_label_factory
        assert my_factory._msg_format is not None
        assert my_factory._msg_format.output_start_tag == "<CUSTOM>"
        assert my_factory._msg_format.output_end_tag == "</CUSTOM>"


class TestJSONExtraction:
    """
    Test class for JSON extraction functionality from message content.

    This class tests the _extract_json method which finds and extracts
    JSON content between specified start and end tags.
    """

    def test_extract_json_valid_content(self,
                                        json_extraction_factory,
                                        valid_content_with_tags):
        """
        Test extraction of JSON from properly formatted message content.

        Should successfully extract JSON string between default tags.
        """
        factory = json_extraction_factory

        result = factory._extract_json(valid_content_with_tags)

        assert result == VALID_JSON_CONTENT
        assert isinstance(result, str)

    def test_extract_json_custom_tags(self, custom_label_factory):
        """
        Test extraction with custom start and end tags.

        Should work with non-default tags from custom MessageFormatConfig.
        """
        factory = custom_label_factory
        content = f"<CUSTOM>{VALID_JSON_CONTENT}</CUSTOM>"

        result = factory._extract_json(content)

        assert result == VALID_JSON_CONTENT

    def test_extract_json_missing_start_tag(self,
                                            json_extraction_factory,
                                            content_missing_start_tag):
        """
        Test behavior when start tag is missing from content.

        Should raise ValueError when output start tag is not found.
        """
        factory = json_extraction_factory

        with pytest.raises(ValueError, match="Message content does not contain "
                                             "valid output tags"):
            factory._extract_json(content_missing_start_tag)

    def test_extract_json_missing_end_tag(self,
                                          json_extraction_factory,
                                          content_missing_end_tag):
        """
        Test behavior when end tag is missing from content.

        Should raise ValueError when output end tag is not found.
        """
        factory = json_extraction_factory

        with pytest.raises(ValueError, match="Message content does not contain "
                                             "valid output tags"):
            factory._extract_json(content_missing_end_tag)

    def test_extract_json_missing_both_tags(self,
                                            json_extraction_factory,
                                            content_missing_both_tags):
        """
        Test behavior when both start and end tags are missing.

        Should raise ValueError when neither tag is found.
        """
        factory = json_extraction_factory

        with pytest.raises(ValueError, match="Message content does not contain "
                                             "valid output tags"):
            factory._extract_json(content_missing_both_tags)

    def test_extract_json_start_before_end(self, json_extraction_factory):
        """
        Test extraction when start tag appears after end tag in content.

        Should raise ValueError if start tag appears after end tag.
        """
        factory = json_extraction_factory
        invalid_content = "first</OUTPUT>some text<OUTPUT> more text"

        with pytest.raises(ValueError, match="Start tag must appear before end "
                                             "tag in message content"):
            factory._extract_json(invalid_content)

    def test_extract_json_nested_tags(self, json_extraction_factory):
        """
        Test extraction when content contains the same tags within the
        extracted section.

        Should raise a value error if nested tags are found.
        """
        factory = json_extraction_factory
        nested_content = "<OUTPUT>first <OUTPUT>nested</OUTPUT> second</OUTPUT>"

        with pytest.raises(ValueError, match="Message content contains "
                                             "multiple start or end tags"):
            factory._extract_json(nested_content)

    def test_extract_json_empty_content_between_tags(self,
                                                     json_extraction_factory,
                                                     content_with_empty_tags):
        """
        Test extraction when content between tags is empty or whitespace.

        Should return an empty string.
        """
        factory = json_extraction_factory

        result = factory._extract_json(content_with_empty_tags)

        assert result == ""
        assert isinstance(result, str)

    def test_extract_json_whitespace_handling(self,
                                              json_extraction_factory,
                                              content_with_whitespace):
        """
        Test that extracted JSON has whitespace properly stripped.

        Should remove leading/trailing whitespace from extracted content.
        """
        factory = json_extraction_factory

        result = factory._extract_json(content_with_whitespace)

        expected = WHITESPACE_JSON_CONTENT.strip()
        assert result == expected
        assert not result.startswith(' ')
        assert not result.endswith(' ')


class TestJSONParsing:
    """
    Test class for JSON parsing and data extraction functionality.

    This class tests the _parse_output method which parses extracted JSON
    strings and extracts keywords and tags data.
    """

    def test_parse_valid_json(self):
        """
        Test parsing of valid JSON containing both keywords and tags arrays.

        Should successfully parse and return dict with keywords and tags lists.
        """
        output = LabelFactory._parse_output(VALID_JSON_CONTENT)
        assert output["tags"] == ["tag1", "tag2"]
        assert output["keywords"] == ["test1", "test2"]

    def test_parse_json_missing_fields(self):
        """
        Test parsing JSON that lacks a keywords or tags field or both.

        Should return json dict with an empty list for the respective missing
        field.
        """
        output = LabelFactory._parse_output("{}")
        assert output["tags"] == []
        assert output["keywords"] == []

        output = LabelFactory._parse_output('{"keywords": ["keyword 1"]}')
        assert output["tags"] == []
        assert output["keywords"] == ["keyword 1"]

        output = LabelFactory._parse_output('{"tags": ["tag 1"]}')
        assert output["tags"] == ["tag 1"]
        assert output["keywords"] == []

    def test_parse_json_extra_fields(self):
        """
        Test parsing JSON that contains additional unexpected fields.

        Should handle extra fields gracefully and extract only required data.
        """
        output = LabelFactory._parse_output("{\"unexpected field\": [1,2,3],"
                                            "\"tags\": [\"标签1\", \"标签2\"],"
                                            "\"keywords\":[\"关键词1\"],"
                                            "\"unexpcted field 2\": [\"a\"]}")
        assert output["tags"] == ["标签1", "标签2"]
        assert output["keywords"] == ["关键词1"]

    def test_malformed_json(self):
        """
        Test parsing string containing malformed string.

        Should raise a ValueError
        """
        with pytest.raises(ValueError, match="Invalid JSON format"):
            LabelFactory._parse_output("not a json")


class TestLabelDataCreation:
    """
    Test class for end-to-end label data creation functionality.

    This class tests the make_label_data method which orchestrates the entire
    process from message parsing to LabelData object creation.
    """

    def test_make_label_data_valid_message(self):
        """
        Test creation of LabelData from a valid message with proper format.

        Should successfully create LabelData object with extracted keywords
        and tags.
        """
        pass

    def test_make_label_data_custom_format_config(self):
        """
        Test label data creation using custom message format configuration.

        Should work with non-default output tags in message format.
        """
        pass
