from __future__ import annotations

from label_generator.label_data import LabelData
from label_generator.response_object import Message


class LabelFactory:
    """
    A class to parse a message object and return labels in a structured format.
    """

    @staticmethod
    def make_label_data(message: Message) -> LabelData:
        """
        Parse the message and return a LabelData object containing keywords
        and tags extracted.
        """
        pass
