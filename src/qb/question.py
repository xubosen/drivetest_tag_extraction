from typing import Set, Tuple, Optional, List
from pydantic import BaseModel, Field, field_validator
import os

class Question(BaseModel):
    """
    Pydantic model for a question with automatic validation.
    """
    qid: str = Field(..., min_length=1,
                     description="Unique identifier for the question")
    chapter: Tuple[int, str] = Field(default=(0, ""),
                                     description="Chapter information as "
                                                 "(number, name)")
    question: str = Field(..., min_length=1,
                          description="The text of the question")
    img_path: str | None = Field(default=None,
                                 description="Optional path to an image "
                                             "associated with the question")
    answers: Set[str] = Field(..., min_length=2,
                              description="Set of possible answers")
    correct_answer: str = Field(..., min_length=1,
                                description="The correct answer to the "
                                            "question")
    tags: List[str] = Field(default_factory=list,
                            description="List of tags associated with the "
                                        "question")
    keywords: List[str] = Field(default_factory=list,
                                description="List of keywords associated with "
                                            "the question")

    @field_validator("chapter", mode="after")
    @classmethod
    def validate_class(cls, chapter: Tuple[int, str]) -> Tuple[int, str]:
        """Validate that chapter is a tuple of (int, str)."""
        if chapter[0] <= 0:
            raise ValueError("Chapter number must be a positive integer")
        if not chapter[1].strip():
            raise ValueError("Chapter name must be a non-empty string")
        return chapter

    @field_validator("img_path")
    @classmethod
    def validate_img_path(cls, path: Optional[str]) -> Optional[str]:
        """Validate that img_path is either None or a valid path string."""
        if path is not None and not os.path.exists(path):
            raise ValueError(f"Image path does not exist: {path}")
        return path

    @field_validator('tags', 'keywords')
    @classmethod
    def validate_string_lists(cls, items: List[str]) -> List[str]:
        """
        Validate that all items in tags/keywords are non-empty strings.
        If duplicates or invalid items are found, they are removed.
        """
        validated_items = []
        for item in items:
            stripped_item = item.strip()
            if len(stripped_item) < 1:
                raise ValueError("Tags and keywords must be non-empty strings")
            if stripped_item not in validated_items:
                validated_items.append(stripped_item)
        return validated_items

    def get_qid(self) -> str:
        """Get the unique identifier of the question."""
        return self.qid

    def get_question(self) -> str:
        """Get the text content of the question."""
        return self.question

    def get_answers(self) -> Set[str]:
        """Get the set of possible answers for the question."""
        return self.answers.copy()

    def get_correct_answer(self) -> str:
        """Get the correct answer for the question."""
        return self.correct_answer

    def has_img(self) -> bool:
        """Check if the question has an associated image."""
        return self.img_path is not None

    def get_img_path(self) -> str | None:
        """Get the path to the image associated with the question, if any."""
        return self.img_path

    def set_img_path(self, img_path: str | None):
        """Set the path to the image associated with the question."""
        self.img_path = img_path

    def get_chapter(self) -> Tuple[int, str]:
        """Get the chapter information for this question."""
        return self.chapter

    def set_chapter(self, chapter: Tuple[int, str]):
        """Set the chapter information for this question."""
        self.chapter = chapter

    def get_tags(self) -> List[str]:
        """Get the list of tags associated with this question."""
        return self.tags.copy()

    def set_tags(self, tags: List[str]):
        """Set the list of tags associated with this question."""
        self.tags = tags.copy()

    def add_tag(self, tag: str):
        """Add a single tag to the question's existing tags."""
        if tag not in self.tags:
            self.tags.append(tag)
        self.tags = self.validate_string_lists(self.tags)

    def get_keywords(self) -> List[str]:
        """Get the list of keywords associated with this question."""
        return self.keywords.copy()

    def set_keywords(self, keywords: List[str]):
        """Set the list of keywords associated with this question."""
        self.keywords = keywords.copy()

    def add_keyword(self, keyword: str):
        """Add a single keyword to the question's existing keywords."""
        if keyword not in self.keywords:
            self.keywords.append(keyword)
        self.keywords = self.validate_string_lists(self.keywords)

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = 'forbid'
