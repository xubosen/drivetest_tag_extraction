from __future__ import annotations
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class LabelData(BaseModel):
    """
    A class to represent the label data extracted from a response.
    """
    model_config = ConfigDict(validate_assignment=True,
                              extra='forbid')
    keywords: List[str] = Field(default_factory=list, min_length=1,
                                description="List of keywords extracted from"
                                            " the response")
    tags: List[str] = Field(default_factory=list, min_length=1,
                            description="List of tags extracted from the "
                                        "response")

    def __init__(self, tags: List[str] = None, keywords: List[str] = None):
        """
        Initialize the LabelData with optional tags and keywords.
        """
        if tags is not None:
            tags = list(set(tags))
        if keywords is not None:
            keywords = list(set(keywords))
        super().__init__(tags=tags, keywords=keywords)

    def add_tags(self, tags: List[str]):
        """
        Add tags to the label data, ensuring no duplicates.
        """
        for tag in tags:
            if tag not in self.tags:
                self.tags.append(tag)

    def get_tags(self) -> List[str]:
        """
        Return the list of tags.
        """
        return self.tags.copy()

    def add_keywords(self, keywords: List[str]):
        """
        Add keywords to the label data, ensuring no duplicates.
        """
        for keyword in keywords:
            if keyword not in self.keywords:
                self.keywords.append(keyword)

    def get_keywords(self) -> List[str]:
        """
        Return the list of keywords.
        """
        return self.keywords.copy()

    def extend(self, label_data: LabelData) -> None:
        """
        Extend the label data with another instance of LabelData,
        """
        self.add_tags(label_data.get_tags())
        self.add_keywords(label_data.get_keywords())
