from typing import Any, Dict, Self, Set, List
import os
from pydantic import BaseModel, Field, field_validator, model_validator

from entities.question import Question

class QuestionBank(BaseModel):
    """
    A Pydantic model to manage a collection of questions with validation.
    """
    img_dir: str = Field(..., min_length=1)
    qids: Set[str] = Field(default_factory=set)
    chapters: Dict[int, str] = Field(default_factory=dict)
    chap_num_to_ids: Dict[int, Set[str]] = Field(default_factory=dict)
    id_to_q: Dict[str, Question] = Field(default_factory=dict)

    @field_validator("qids")
    @classmethod
    def validate_qids(cls, qids: Set[str]) -> Set[str]:
        """
        Validate that question IDs are non-empty strings.

        :param qids: Set of question IDs
        :return: Validated set of question IDs
        :raises ValueError: If any ID is empty or not a string
        """
        if "" in qids:
            raise ValueError("All question IDs must be non-empty strings")
        return qids

    @field_validator("chapters")
    @classmethod
    def validate_chapters(cls, chapters: Dict[int, str]) -> Dict[int, str]:
        """
        Validate that chapter numbers are positive integers and names are
        non-empty strings.

        :param chapters: Dictionary of chapter numbers and their descriptions
        :return: Validated dictionary of chapters
        :raises ValueError: If any chapter number is not a positive integer or
        name is empty
        """
        for chap_num, description in chapters.items():
            if chap_num <= 0:
                raise ValueError(f"Chapter number must be a positive integer:"
                                 f" {chap_num}")
            if not description.strip():
                raise ValueError(f"Chapter description cannot be empty for"
                                 f" chapter {chap_num}")
        return chapters

    @field_validator("img_dir")
    @classmethod
    def validate_img_dir(cls, img_dir: str) -> str:
        """
        Validate that the image directory exists and is a directory.

        :param img_dir: Path to the image directory
        :return: Validated image directory path
        :raises ValueError: If the directory does not exist or is not a directory
        """
        img_dir = img_dir.strip()
        if not os.path.exists(img_dir) or not os.path.isdir(img_dir):
            raise ValueError(f"Image directory does not exist or is not a "
                             f"directory: {img_dir}")
        return img_dir

    @model_validator(mode='after')
    def validate_chapter_consistency(self):
        if not self.chap_num_to_ids.keys() == self.chapters.keys():
            raise ValueError("Chapter numbers must match")
        for qid in self.qids:
            count = sum(
                1 for ids in self.chap_num_to_ids.values() if qid in ids)
            if count != 1:
                raise ValueError(
                    f"Question {qid} must belong to exactly one chapter")
        return self

    def add_chapter(self, chapter_num: int, description: str):
        """
        Add a new chapter to the question bank.

        :param chapter_num: Unique identifier for the chapter
        :param description: Description of the chapter content
        :raises ValueError: If the chapter number already exists
        """
        if chapter_num not in self.chapters:
            self.chapters[chapter_num] = description
            self.chap_num_to_ids[chapter_num] = set()
        self.validate_chapters(self.chapters)

    def add_question(self, question: Question, chapter_num: int):
        """
        Add a question to the question bank and associate it with a chapter.

        :param question: The Question to add
        :param chapter_num: The chapter number to associate with this question
        :raises KeyError: If the chapter number does not exist
        """
        if chapter_num not in self.chapters:
            raise KeyError(f"Chapter {chapter_num} does not exist")

        self.qids.add(question.get_qid())
        self.chap_num_to_ids[chapter_num].add(question.get_qid())
        self.id_to_q[question.get_qid()] = question

    def get_question(self, q_id: str) -> Question:
        """
        Retrieve a question by its ID.

        :param q_id: The ID of the question to retrieve
        :return: The Question object
        :raises LookupError: If the question ID is not found
        """
        if q_id in self.qids:
            return self.id_to_q[q_id]
        else:
            raise LookupError(f"Question {q_id} not found")

    def get_qids_by_chapter(self, chap_num: int) -> Set[str]:
        """
        Get all question IDs associated with a specific chapter.

        :param chap_num: The chapter number
        :return: A set of question IDs
        :raises LookupError: If the chapter number is not found
        """
        if chap_num in self.chapters.keys():
            return self.chap_num_to_ids[chap_num].copy()
        else:
            raise LookupError(f"Chapter {chap_num} not found")

    def describe_chapter(self, chap_num: int) -> str:
        """
        Get the description of a chapter.

        :param chap_num: The chapter number
        :return: The chapter description
        :raises LookupError: If the chapter number is not found
        """
        if chap_num in self.chapters.keys():
            return self.chapters[chap_num]
        else:
            raise LookupError(f"Chapter {chap_num} not found")

    def get_img_dir(self) -> str:
        """
        Get the directory path where question images are stored.

        :return: Path to the image directory
        """
        return self.img_dir

    def set_img_dir(self, img_dir: str):
        """Set the image directory with validation"""
        self.img_dir = img_dir.strip()

    def list_chapters(self) -> List[int]:
        """
        Return an ordered list of chapter numbers
        :return: An ordered list of chapter numbers
        """
        return sorted(self.chapters.keys())

    def get_qid_list(self) -> List[str]:
        """
        Return an ordered list of question ids
        """
        return sorted(self.qids)

    def question_count(self, chapter_num: int = None) -> int:
        """
        Count the number of questions.

        :param chapter_num: Optional chapter to count questions from
        :return: Number of questions
        """
        return len(self.qids) if chapter_num is None \
            else len(self.chap_num_to_ids[chapter_num])

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        """
        Validate an object against the model.

        :param obj: The object to validate
        :return: An instance of QuestionBank if validation is successful
        """
        try:
            for item in obj:
                if item not in cls.model_fields:
                    raise ValueError(f"Unexpected field: {item}")
            if "img_dir" not in obj.keys():
                raise ValueError("Missing required field: img_dir")

            qids = obj["qids"] if "qids" in obj else set()
            chapters = obj["chapters"] if "chapters" in obj else {}
            chap_num_to_ids = obj["chap_num_to_ids"] if ("chap_num_to_ids"
                                                          in obj) else {}
            id_to_q = obj["id_to_q"] if "id_to_q" in obj else {}

            return QuestionBank(
                img_dir=obj["img_dir"],
                qids=qids,
                chapters=chapters,
                chap_num_to_ids=chap_num_to_ids,
                id_to_q=id_to_q
            )
        except Exception as e:
            raise ValueError(f"Validation failed: {e}")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = 'forbid'
