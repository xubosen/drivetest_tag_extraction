import base64
from logging import Logger
from typing import Dict, List, Any, Set

from entities.question import Question
from entities.question_bank import QuestionBank
from label_generator.labeling_request import LabelingRequest
from label_generator.batch_request import LabelingBatchRequest

class BatchRequestMaker:
    """
    A Pydantic model to format the question bank into a batch request object
    specified by the OpenAI API for batch processing.
    """
    _qb: QuestionBank
    _prompt: str
    _logger: Logger

    def __init__(self, question_bank: QuestionBank, model_name: str,
                 prompt: str, logger: Logger):
        self._qb = question_bank
        self._model = model_name
        self._prompt = prompt
        self._logger = logger

    def make_batch_request(self) -> LabelingBatchRequest:
        """
        Creates a JSONL file from the QuestionBank instance and save it to the
        specified file path.
        """
        self._logger.info(f"Starting batch request creation. "
                          f"Processing {self._qb.question_count()} questions.")

        requests_lst = []
        processed_count = 0
        for qid in self._qb.get_qid_list():
            requests_lst.append(self._make_request(self._qb.get_question(qid)))

            if processed_count % 100 == 0:
                self._logger.info(f"Processed {processed_count}/"
                                 f"{self._qb.question_count()} questions")

        batch_request = LabelingBatchRequest(requests=requests_lst)

        self._logger.info(f"Successfully created batch request.")
        return batch_request

    def _make_request(self, question: Question) -> LabelingRequest:
        self._logger.debug(f"Creating request for question {question.get_id()}")

        request = LabelingRequest(custom_id=question.get_qid(),
                                  model=self._model,
                                  prompt=self._prompt,
                                  content=self._make_content(question))

        self._logger.debug(f"Successfully created request for question "
                          f"{question.get_id()}")
        return request

    def _make_content(self, question: Question) -> List[Dict[str, Any]]:
        if question.get_img_path() is not None:
            self._logger.debug(f"Processing question with image: "
                              f"{question.get_img_path()}")
            return [{"type": "image",
                     "image": self._format_image(question.get_img_path())},
                    {"type": "text",
                     "text": self._question_to_dict(question)}]
        else:
            self._logger.debug("Processing text-only question")
            return [{"type": "text", "text": self._question_to_dict(question)}]

    def _format_image(self, img_path: str) -> str:
        """
        Encode the image to Base64.

        :param img_path: Path to the image file.
        :return: Base64 encoded image.
        """
        self._logger.debug(f"Encoding image to Base64: {img_path}")
        try:
            with open(img_path, 'rb') as image_file:
                encoded_image = base64.b64encode(
                    image_file.read()
                ).decode('utf-8')
                self._logger.debug(f"Successfully encoded image: {img_path} "
                                  f"(size: {len(encoded_image)} chars)")
                return f"data:image/jpeg;base64,{encoded_image}"
        except Exception as e:
            error_msg = f"Failed to encode image {img_path}: {str(e)}"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

    def _question_to_dict(self, question: Question) -> Dict[str, Any]:
        """
        Format the question into a dictionary representation.
        """
        self._logger.debug("Converting question to dictionary format")
        try:
            dict_question = {
                "章节": f"{question.get_chapter()[0]}: "
                        f"{question.get_chapter()[1]}",
                "题目": question.get_question(),
                "选项": self._assign_letter_codes(question.get_answers()),
                "答案": question.get_correct_answer()
            }
            self._logger.debug(f"Question converted to dict with "
                              f"{len(dict_question['选项'])} answer choices")
            return dict_question
        except Exception as e:
            error_msg = (f"Failed to convert question {question.get_id()}: "
                         f"{str(e)}")
            self._logger.error(error_msg)
            raise ValueError(error_msg)

    def _assign_letter_codes(self, answer_choices: Set[str]) -> Dict[str, str]:
        """
        Assigns letter codes (A, B, C, ...) to the answer choices.
        """
        self._logger.debug(f"Assigning letter codes to {len(answer_choices)} "
                          f"answer choices")

        answer_choices_lst = sorted(list(answer_choices))
        lettered_choices = {}
        for i in range(0, len(answer_choices_lst)):
            letter_code = chr(ord('A') + i)
            lettered_choices[letter_code] = answer_choices_lst[i]

        self._logger.debug(f"Successfully assigned letter codes: "
                          f"{list(lettered_choices.keys())}")
        return lettered_choices
