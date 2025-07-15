# Data class for a question
from typing import Set, Tuple

class Question:
    """
    Dataclass for a question.
    """
    _qid: str
    _question: str
    _img_path: str | None
    _answers: Set[str]
    _correct_answer: str
    _tags: list[str]
    _chapter: Tuple[int, str]

    def __init__(self, qid: str, question: str, answers: Set[str],
                 correct_answer: str, img_path: str | None = None,
                 tags: list[str] = None, chapter: Tuple[int, str] = None):
        """
        Initializes the Question with the provided parameters.

        :param qid: Unique identifier for the question.
        :param question: The text of the question.
        :param answers: Set of possible answers.
        :param correct_answer: The correct answer to the question.
        :param img_path: Optional path to an image associated with the question.
        """
        self._qid = qid
        self._question = question
        self._answers = answers
        self._correct_answer = correct_answer
        self._img_path = img_path
        self._tags = [] if tags is None else tags
        self._chapter = "" if chapter is None else chapter
        self._check_format()

    def _check_format(self):
        """
        Check if the question format is correct and raise an error if not.

        Validates that:
        - Question ID is a non-empty string
        - Question text is a non-empty string
        - There are at least two answer options
        - No answer is an empty string
        - The correct answer is one of the provided answers
        - Image path is either None or a string

        :raises IncorrectFormatError: If any validation fails
        """
        if not isinstance(self._qid, str) or not self._qid:
            raise IncorrectFormatError("Question ID must be a non-empty string.")
        if not isinstance(self._question, str) or not self._question:
            raise IncorrectFormatError("Question text must be a non-empty string.")
        if not isinstance(self._answers, set) or len(self._answers) < 2:
            raise IncorrectFormatError("There must be at least two answers.")
        if "" in self._answers or '' in self._answers:
            raise IncorrectFormatError("Answers cannot contain empty strings.")
        if not isinstance(self._correct_answer, str) or self._correct_answer not in self._answers:
            raise IncorrectFormatError("Correct answer must be one of the provided answers.")
        if self._img_path is not None and not isinstance(self._img_path, str):
            raise IncorrectFormatError("Image path must be a string or None.")

    def get_qid(self) -> str:
        """
        Get the unique identifier of the question.

        :return: The question ID as a string
        """
        return self._qid

    def get_question(self) -> str:
        """
        Get the text content of the question.

        :return: The question text as a string
        """
        return self._question

    def get_answers(self) -> Set[str]:
        """
        Get the set of possible answers for the question.

        :return: A set containing all possible answer strings
        """
        return self._answers

    def get_correct_answer(self) -> str:
        """
        Get the correct answer for the question.

        :return: The correct answer as a string
        """
        return self._correct_answer

    def get_img_path(self) -> str | None:
        """
        Get the path to the image associated with the question, if any.

        :return: The image path as a string, or None if no image is associated
        """
        return self._img_path

    def set_img_path(self, img_path: str | None):
        """
        Set the path to the image associated with the question.

        :param img_path: The new image path as a string, or None if no image is associated
        """
        if img_path is not None and not isinstance(img_path, str):
            raise IncorrectFormatError("Image path must be a string or None.")
        self._img_path = img_path

    def set_chapter(self, chapter: Tuple[int, str]):
        """
        Set the chapter information for this question.

        :param chapter: A tuple containing chapter number and chapter name
        """
        self._chapter = chapter

    def get_chapter(self) -> Tuple[int, str]:
        """
        Get the chapter information for this question.

        :return: A tuple containing chapter number and chapter name
        """
        return self._chapter

    def get_tags(self) -> list[str]:
        """
        Get the list of tags associated with this question.

        :return: List of tag strings
        """
        return self._tags.copy()

    def set_tags(self, tags: list[str]):
        """
        Set the list of tags associated with this question.

        :param tags: List of tag strings to associate with this question
        """
        self._tags = tags.copy()

    def add_tag(self, tag: str):
        """
        Add a single tag to the question's existing tags.

        :param tag: Tag string to add to the question
        """

        self._tags.append(tag)


class IncorrectFormatError(TypeError):
    """ Error class for incorrect question format. """

    def __init__(self, message: str):
        """
        Initializes the IncorrectFormatError with a message.

        :param message: Error description message
        """
        super().__init__(message)
