import json
import os
from typing import Dict, Any

from qb.question_bank import QuestionBank
from qb.question import Question


class LocalJsonDB:
    """
    A class for retrieving a question bank from a local JSON file.
    """
    _db_file_path: str
    _img_dir: str

    def __init__(self, db_file_path: str, img_dir: str):
        """
        Initialize the LocalJsonDB with paths for JSON file and image directory.
        """
        self._db_file_path = db_file_path
        self._img_dir = img_dir

    def load(self) -> QuestionBank:
        """
        Load a question bank from the database.

        :return: The question bank stored in the database
        :raises FileNotFoundError: If the database file doesn't exist
        """
        if not os.path.exists(self._db_file_path):
            raise FileNotFoundError(f"Database file not found: "
                                    f"{self._db_file_path}")

        try:
            # Read the JSON file
            with open(self._db_file_path, 'r') as f:
                data = json.load(f)

            # Convert from serialized format to QuestionBank
            return self._deserialize_question_bank(data)
        except Exception as e:
            raise RuntimeError(f"Error loading question bank: {e}")

    def _deserialize_question_bank(self, data: Dict[str, Any]) -> QuestionBank:
        """
        Convert a serialized dictionary back to a QuestionBank.

        :param data: Dictionary containing serialized QuestionBank data
        :return: Reconstructed QuestionBank
        """
        # Create a new QuestionBank
        qb = QuestionBank(self._img_dir)

        # If the database is empty, return an empty QuestionBank
        if not data.get("chapters"):
            return qb

        # Add chapters
        for chap_num_str, description in data["chapters"].items():
            chap_num = int(chap_num_str)
            qb.add_chapter(chap_num, description)

        # Add questions
        for qid, q_data in data["questions"].items():
            # Find which chapter this question belongs to
            chapter_num = None
            for chap_num_str, qids in data["chap_to_qids"].items():
                if qid in qids:
                    chapter_num = int(chap_num_str)
                    break

            if chapter_num is not None:
                img_path = q_data["img_path"]
                # Check if the image path is valid
                if (not os.path.exists(img_path)) or (not img_path):
                    img_path = None

                # Create the Question object
                question = Question(
                    qid=q_data["qid"],
                    question=q_data["question"],
                    answers=set(q_data["answers"]),
                    correct_answer=q_data["correct_answer"],
                    img_path=img_path
                )

                # Add to QuestionBank
                qb.add_question(question, chapter_num)
        return qb
