import os

from data_storage.database.database_interface import Database
from data_storage.database.local_json_db import LocalJsonDB
from qb.question_bank import QuestionBank
from data_cleaning.img_reshaper import ImgReshaper

class DataFormatter:
    """
    Formats the question bank object for automatic labeling.
    """

    def __init__(self, image_reshaper: ImgReshaper):
        """
        Initializes the DataFormatter with the output directory.
        """
        self._reshaper = image_reshaper

    def format_data(self, data: Database, output_directory: str) -> QuestionBank:
        """
        Formats the question bank for automatic labeling.
        """
        qb = data.load()
        file_dir = os.path.join(output_directory, "data.json")
        img_dir = os.path.join(output_directory, "images")

        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        self._resize_images(qb=qb, new_img_dir=img_dir)
        self._set_up_question_chapters(qb)
        new_db = LocalJsonDB(db_file_path=file_dir, img_dir=img_dir)
        new_db.save(qb)
        return qb

    def _resize_images(self, qb: QuestionBank, new_img_dir: str) -> None:
        """ Resize images in the question bank and update their paths. """
        for qid in qb.get_qid_list():
            question = qb.get_question(qid)
            if question.get_img_path() is not None:
                new_path = self._reshaper.reshape(qid, qb.get_img_dir(),
                                                  new_img_dir)
                question.set_img_path(new_path)
        qb.set_img_dir(new_img_dir)

    def _set_up_question_chapters(self, qb: QuestionBank):
        for chapter_id in qb.list_chapters():
            for qid in qb.get_qids_by_chapter(chapter_id):
                question = qb.get_question(qid)
                question.set_chapter((chapter_id,
                                      qb.describe_chapter(chapter_id)))
