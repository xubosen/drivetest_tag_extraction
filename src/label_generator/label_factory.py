from __future__ import annotations

from label_generator.label_data import LabelData
from label_generator.response_object import Message

THINKING_START_TAG = '<THINKING>'
THINKING_END_TAG = '</THINKING>'
OUTPUT_START_TAG = '<OUTPUT>'
OUTPUT_END_TAG = '</OUTPUT>'

THINKING_OUTPUT_START_TAG = '**第二步：生成JSON**'
THINKING_OUTPUT_END_TAG = '</THINKING>'


class LabelFactory:
    """
    A class to parse a message object and return labels in a structured format.
    """

    def make_label_data(self, message: Message) -> LabelData:
        """
        Parse the message and return a LabelData object containing keywords
        and tags extracted.
        """
        KEYWORDS_TAG = '\"keywords\": [\n'
        TAGS_TAG = '\n],\n\"tags\": [\n'
        TAGS_END = '\n]\n}\n'

        message_text = message.content

        keywords_start = message_text.rfind(KEYWORDS_TAG) + len(KEYWORDS_TAG)
        keywords_end = message_text.rfind(TAGS_TAG)
        tags_start = message_text.rfind(TAGS_TAG) + len(TAGS_TAG)
        tags_end = message_text.rfind(TAGS_END)

        str_keywords = message_text[keywords_start:keywords_end].split(",")
        str_tags = message_text[tags_start:tags_end].split(",")

        keywords = []
        tags = []
        for keyword in str_keywords:
            keywords.append(keyword[1:-1])
        for tag in str_tags:
            tags.append(tag[1:-1])

        return LabelData(keywords=keywords, tags=tags)

    # def _remove_line_break(self, message: str) -> str:
    #     """ Remove all line breaks (\n) """
    #
    #
    #
    # def _get_thinking(self, message_text: str) -> str:
    #     """
    #
    #     """
    #     start_pos = (message_text.find(THINKING_START_TAG)
    #                  + len(THINKING_START_TAG))
    #     end_pos = message_text.find(THINKING_END_TAG)
    #     return message_text[start_pos:end_pos]
    #
    #
    # def _get_output_from_thinking(self, thinking_text: str) -> str:
    #     """
    #
    #     """
    #     start_pos = thinking_text.find(OUTPUT_START_TAG)
    #
    #
    # def _get_output(self, message_text: str) -> str:
    #     """
    #
    #     """
    #     start_pos = message_text.find(OUTPUT_START_TAG) + len(OUTPUT_END_TAG)
    #     end_pos = message_text.find(OUTPUT_END_TAG)
    #     return message_text[start_pos:end_pos]
