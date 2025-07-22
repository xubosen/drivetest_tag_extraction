import base64
from logging import Logger
import os
from typing import Dict, List, Any, Set
from pydantic import BaseModel, Field, ValidationError

from entities.question import Question
from entities.question_bank import QuestionBank

class BatchRequest(BaseModel):
    """Pydantic model for a batch request entry."""
    custom_id: str = Field(..., min_length=1)
    method: str = Field(default="POST")
    url: str = Field(default="/v1/chat/completions")
    body: Dict[str, Any] = Field(...)
    # TODO: Validate the body structure more rigorously

class BatchFileMaker(BaseModel):
    """
    A Pydantic model to format the question bank into a json file with format
    specified by the OpenAI API for batch processing.
    """
    qb: QuestionBank = Field(..., description="QuestionBank instance containing"
                                              " questions")
    prompt: str = Field(..., min_length=1, description="System prompt for the"
                                                       " API")
    logger: Logger = Field(..., description="Logger instance for logging")

    def make_batch_file(self, file_path: str) -> None:
        """
        Creates a JSONL file from the QuestionBank instance and save it to the
        specified file path.
        """
        self.logger.info(f"Starting batch file creation at: {file_path}")
        self._check_file_path(file_path)

        self.logger.info(
            f"Processing {self._qb.question_count()} questions for batch"
            f" file")
        processed_count = 0
        with open(file_path, 'w', encoding='utf-8') as file:
            for qid in self.qb.get_qid_list():
                self.logger.debug(f"Processing question {qid} "
                                  f"({processed_count + 1}/"
                                  f"{self._qb.question_count()})")
                try:
                    batch_request = self._question_to_batch_request(
                        self.qb.get_question(qid), qid)
                    jsonl_line = batch_request.model_dump_json(exclude_none=
                                                               True)
                    file.write(jsonl_line + '\n')
                    processed_count += 1

                except ValidationError as e:
                    error_msg = f"Invalid question data for ID {qid}: {e}"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

                if processed_count % 100 == 0:
                    self.logger.info(f"Processed {processed_count}/"
                                     f"{self._qb.question_count()} questions")

        self.logger.info(f"Successfully created batch file with "
                         f"{processed_count} questions at: {file_path}")

    def _check_file_path(self, file_path: str):
        """
        Check if the file path exists and is a jsonl file.
        """
        self.logger.debug(f"Validating file path: {file_path}")

        error_msg = None
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            error_msg = f"Directory does not exist: {directory}"
        if not file_path.lower().endswith('.jsonl'):
            error_msg = f"Invalid file path: {file_path}"
        if not os.path.isfile(file_path):
            error_msg = f"The file {file_path} does not exist."

        if error_msg is not None:
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        else:
            self.logger.debug(f"File path validation successful: {file_path}")

    def _question_to_batch_request(self,
                                   question: Question,
                                   qid: str) -> BatchRequest:
        """
        Formats a question into a BatchRequest model.

        :param question: An instance of Question.
        :param qid: A unique identifier for the question.
        :return: A BatchRequest model representing the question entry.
        """
        self.logger.debug(f"Converting question {qid} to batch request format")
        batch_request = BatchRequest(
            custom_id=qid,
            method="POST",
            url="/v1/chat/completions",
            body={
                "model": "qwen-vl-max",
                "messages": self._make_message(question)
            }
        )

        self.logger.debug(f"Successfully converted question {qid} to batch "
                          f"request format")
        return batch_request

    def _make_message(self, question: Question) -> List[Dict[str, Any]]:
        return [{"role": "system", "content": self.prompt},
                {"role": "user", "content": self._make_content(question)}]

    def _make_content(self, question: Question) -> List[Dict[str, Any]]:
        if question.get_img_path() is not None:
            self.logger.debug(f"Processing question with image: "
                              f"{question.get_img_path()}")
            return [{"type": "image",
                     "image": self._format_image(question.get_img_path())},
                    {"type": "text",
                     "text": self._question_to_dict(question)}]
        else:
            self.logger.debug("Processing text-only question")
            return [{"type": "text", "text": self._question_to_dict(question)}]

    def _format_image(self, img_path: str) -> str:
        """
        Encode the image to Base64.

        :param img_path: Path to the image file.
        :return: Base64 encoded image.
        """
        self.logger.debug(f"Encoding image to Base64: {img_path}")
        try:
            with open(img_path, 'rb') as image_file:
                encoded_image = base64.b64encode(
                    image_file.read()
                ).decode('utf-8')
                self.logger.debug(f"Successfully encoded image: {img_path} "
                                  f"(size: {len(encoded_image)} chars)")
                return f"data:image/jpeg;base64,{encoded_image}"
        except Exception as e:
            error_msg = f"Failed to encode image {img_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def _question_to_dict(self, question: Question) -> Dict[str, Any]:
        """
        Format the question into a dictionary representation.
        """
        self.logger.debug("Converting question to dictionary format")
        try:
            dict_question = {
                "章节": f"{question.get_chapter()[0]}: "
                        f"{question.get_chapter()[1]}",
                "题目": question.get_question(),
                "选项": self._assign_letter_codes(question.get_answers()),
                "答案": question.get_correct_answer()
            }
            self.logger.debug(f"Question converted to dict with "
                              f"{len(dict_question['选项'])} answer choices")
            return dict_question
        except Exception as e:
            error_msg = (f"Failed to convert question {question.get_id()}: "
                         f"{str(e)}")
            self.logger.error(error_msg)
            raise ValueError(error_msg)

    def _assign_letter_codes(self, answer_choices: Set[str]) -> Dict[str, str]:
        """
        Assigns letter codes (A, B, C, ...) to the answer choices.
        """
        self.logger.debug(f"Assigning letter codes to {len(answer_choices)} "
                          f"answer choices")

        answer_choices_lst = sorted(list(answer_choices))
        lettered_choices = {}
        for i in range(0, len(answer_choices_lst)):
            letter_code = chr(ord('A') + i)
            lettered_choices[letter_code] = answer_choices_lst[i]

        self.logger.debug(f"Successfully assigned letter codes: "
                          f"{list(lettered_choices.keys())}")
        return lettered_choices

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True  # Allow Logger type
        validate_assignment = True
