from __future__ import annotations
from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class LabelData(BaseModel):
    """
    A class to represent the label data extracted from a response.
    """
    model_config = ConfigDict(validate_assignment=True,
                              extra='forbid')
    keywords: List[str] = Field(default_factory=list,
                                description="List of keywords extracted from"
                                            " the response")
    tags: List[str] = Field(default_factory=list,
                            description="List of tags extracted from the "
                                        "response")

    @field_validator('tags', 'keywords', mode='after')
    @classmethod
    def validate_unique_strings(cls, v: List[str]) -> List[str]:
        """
        Ensure that the tags and keywords are unique strings.
        """
        if not isinstance(v, list):
            raise ValueError("Must be a list")
        if not all(isinstance(item, str) for item in v):
            raise ValueError("All items must be strings")
        if len(set(v)) != len(v):
            v = list(set(v))
        return v

    def __init__(self, tags=None, keywords=None):
        """
        Initialize the LabelData with optional tags and keywords.
        """
        if keywords is None:
            keywords = []
        if tags is None:
            tags = []
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
