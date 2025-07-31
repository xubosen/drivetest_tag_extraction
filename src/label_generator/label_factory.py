from typing import Dict, List
from pydantic import BaseModel, Field, ConfigDict, field_validator, \
    model_validator
import json

from label_generator.label_data import LabelData
from label_generator.response_object import Message


class MessageFormatConfig(BaseModel):
    """
    Configuration for the content format.
    """
    model_config = ConfigDict(validate_assignment=True,
                              extra="forbid",
                              frozen=True)
    output_start_tag: str = Field(min_length=1,
                                  description="Start tag for the output "
                                              "section.")
    output_end_tag: str = Field(min_length=1,
                                description="End tag for the output "
                                            "section.")

    @model_validator(mode='after')
    def validate_tags(self):
        if self.output_start_tag == self.output_end_tag:
            raise ValueError("Start and end tags must be different.")
        return self


class LabelFactory:
    """
    A class to parse a message object and return labels in a structured format.
    """
    _msg_format: MessageFormatConfig = Field(description="Configuration for "
                                                         "the message object.")

    def __init__(self, message_format: MessageFormatConfig):
        """
        Initialize the LabelFactory with a MessageFormatConfig object.
        """
        self._msg_format = message_format

    def make_label_data(self, message: Message) -> LabelData:
        """
        Parse the message and return a LabelData object containing keywords
        and tags extracted.

        ============ Representational Invariant ============
        - message is formatted such that the output json string in enclosed by
        the output_start_tag and output_end_tag from the MessageFormatConfig
        object.
        """
        msg_content = message.content
        json_str = self._extract_json(msg_content)
        parsed_data = self._parse_output(json_str)
        return LabelData(keywords=parsed_data["keywords"],
                         tags=parsed_data["tags"])

    def _extract_json(self, msg_content: str) -> str:
        """
        Extract the json string from the message content.
        """
        start_tag = self._msg_format.output_start_tag
        end_tag = self._msg_format.output_end_tag
        start_index = msg_content.find(start_tag)
        end_index = msg_content.rfind(end_tag)

        if start_index == -1 or end_index == -1:
            raise ValueError("Message content does not contain valid "
                             "output tags.")
        elif start_index >= end_index:
            raise ValueError("Start tag must appear before end tag in "
                             "message content.")

        output_str = msg_content[start_index + len(start_tag):end_index].strip()
        if start_tag in output_str or end_tag in output_str:
            raise ValueError("Message content contains multiple start or end "
                             "tags")
        return msg_content[start_index + len(start_tag):end_index].strip()

    @staticmethod
    def _parse_output(json_str: str) -> Dict[str, List]:
        """
        Parse the JSON string to extract keywords and tags.
        """
        try:
            data = json.loads(json_str)
            keywords = data["keywords"] if "keywords" in data.keys() else []
            tags = data["tags"] if "tags" in data.keys() else []
            return {"keywords": keywords,
                    "tags": tags}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
