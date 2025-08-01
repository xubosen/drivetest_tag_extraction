# Data access object for saving and loading QuestionBank objects from a local
# json file.

import json
import os
import shutil
from typing import Dict, List, Any

from data_access.data_access_interface import Database
from entities.question_bank import QuestionBank
from entities.question import Question


class LocalJsonDB(Database):
    """
    A data access object for storing the question bank in a local JSON file.
    """
    _db_file_path: str
    _img_dir: str

    def __init__(self, db_file_path: str, img_dir: str):
        """
        Initialize the LocalJsonDB with paths for JSON file and image directory.
        """
        self._db_file_path = db_file_path
        self._img_dir = img_dir

    def save(self, qb: QuestionBank) -> bool:
        """
        Save the question bank.

        :param qb: QuestionBank to save
        :return: True if save was successful, False otherwise
        """
        try:
            os.makedirs(self._img_dir, exist_ok=True)
            data = self._serialize_question_bank(qb)
            if self._img_dir != qb.get_img_dir():
                self._copy_images(qb)
            with open(self._db_file_path, 'w') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            raise e

    def load(self) -> QuestionBank:
        """
        Load a question bank from the path specified.

        :return: The question bank stored at the file path.
        :raises FileNotFoundError: If the file doesn't exist
        """
        if not os.path.exists(self._db_file_path):
            raise FileNotFoundError(f"Database file not found: "
                                    f"{self._db_file_path}")
        try:
            with open(self._db_file_path, 'r') as file:
                if file.read().strip() == '{}':
                    return QuestionBank(img_dir=self._img_dir)
                else:
                    file.seek(0)
                    data = json.load(file)
                    return self._deserialize_question_bank(data)
        except Exception as e:
            raise ConnectionError(f"Error loading question bank: {e}")

    def _serialize_question_bank(self, qb: QuestionBank) -> Dict[str, Any]:
        """
        Convert a QuestionBank to a JSON-serializable dictionary.

        :param qb: QuestionBank to serialize
        :return: Dictionary representation of the QuestionBank
        """
        chapters, chapter_to_qids, questions = {}, {}, {}
        for chapter in qb.list_chapters():
            chapters[chapter] = qb.describe_chapter(chapter)
            self._serialize_chapter(chapter, chapter_to_qids, qb, questions)
        return {"chapters": chapters,
                "chap_to_qids": chapter_to_qids,
                "questions": questions,
                "img_dir": self._img_dir}

    def _serialize_chapter(self, chapter: int,
                           chapter_to_qids: Dict[int, List[str]],
                           qb: QuestionBank, questions: Dict[str, Any]):
        chapter_to_qids[chapter] = sorted(list(qb.get_qids_by_chapter(chapter)))
        for qid in chapter_to_qids[chapter]:
            question = qb.get_question(qid)
            questions[qid] = {
                "qid": question.get_qid(),
                "question": question.get_question(),
                "answers": list(question.get_answers()),
                "correct_answer": question.get_correct_answer(),
                "img_path": self._make_img_path(question),
                "chapter": chapter,
                "tags": question.get_tags(),
                "keywords": question.get_keywords()
            }

    def _make_img_path(self, question) -> str:
        if question.get_img_path() is None:
            return ""
        extension = question.get_img_path().split(".")[-1]
        return f"{self._img_dir}/{question.get_qid()}.{extension}"

    def _deserialize_question_bank(self, data: Dict[str, Any]) -> QuestionBank:
        """
        Convert a serialized dictionary back to a QuestionBank.

        :param data: Dictionary containing serialized QuestionBank data
        :return: Reconstructed QuestionBank
        """
        qb = QuestionBank(img_dir=self._img_dir)
        self._add_chapters(data, qb)
        self._add_questions(data, qb)
        return qb

    def _add_questions(self, data, qb):
        for qid, q_data in data["questions"].items():
            chapter = self._get_chapter_num(data, qid)
            img_path = self._get_img_path(q_data)
            question = Question(
                qid=q_data["qid"],
                question=q_data["question"],
                answers=set(q_data["answers"]),
                correct_answer=q_data["correct_answer"],
                img_path=img_path,
                chapter=(chapter, qb.describe_chapter(chapter))
            )
            if "tags" in q_data.keys():
                question.set_tags(q_data["tags"])
                question.set_keywords(q_data["keywords"])
            qb.add_question(question, chapter)

    def _get_img_path(self, q_data):
        img_path = q_data["img_path"]
        if not img_path.strip():
            return None
        elif os.path.exists(img_path):
            return img_path
        else:
            raise FileNotFoundError(
                f"Image file not found: {img_path}. "
            )

    def _get_chapter_num(self, data, qid) -> int:
        # Find which chapter this question belongs to
        chapter_num = None
        for chap_num, qids in data["chap_to_qids"].items():
            if qid in qids:
                chapter_num = int(chap_num)
                break
        if chapter_num is None:
            raise ValueError(f"Question ID {qid} does not belong to any chapter.")
        return chapter_num

    def _add_chapters(self, data, qb):
        # Add chapters
        for chap_num_str, description in data["chapters"].items():
            chap_num = int(chap_num_str)
            qb.add_chapter(chap_num, description)

    def _copy_images(self, qb: QuestionBank) -> None:
        """
        Copy images from the QuestionBank's image directory to the current
        database's image directory.

        :param qb: QuestionBank containing images to copy
        """
        # Get all chapter numbers
        for qid in qb.get_qid_list():
            question = qb.get_question(qid)
            cur_path = question.get_img_path()
            new_path = self._make_img_path(question)

            if cur_path and os.path.exists(cur_path):
                # Copy the image to our image directory
                shutil.copy2(cur_path, new_path)
