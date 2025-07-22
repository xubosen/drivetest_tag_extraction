# Public interface for the raw_database module
from abc import ABC, abstractmethod

from entities.question_bank import QuestionBank


class Database(ABC):
    """
    A raw_database for storing the questionbank
    """

    @abstractmethod
    def save(self, qb: QuestionBank) -> bool:
        """
        Save the question bank to the raw_database.
        :param qb:
        :return: True iff the question bank was saved successfully
        """
        raise NotImplementedError

    @abstractmethod
    def load(self) -> QuestionBank:
        """
        Load a question bank from the raw_database.
        :return: The question bank stored in the raw_database.
        """
        raise NotImplementedError
