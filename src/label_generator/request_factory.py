import base64
from logging import Logger
from typing import Dict, List, Set

from entities.question import Question
from label_generator.labeling_request import LabelingRequest

class RequestFactory:
    """
    A factory class to create labeling requests for individual questions.
    """
    _model: str
    _url: str
    _prompt: str
    _logger: Logger

    def __init__(self, model, url, prompt, logger: Logger):
        """
        Initializes the RequestFactory with model, URL, prompt, and logger.
        """
        self._model = model
        self._url = url
        self._prompt = prompt
        self._logger = logger

    def make_request(self,
                     question: Question,
                     custom_id: str) -> LabelingRequest:
        """
        Creates a labeling request for a given question.
        """
        self._logger.debug(f"Creating request")

        request = LabelingRequest(custom_id=custom_id,
                                  model=self._model,
                                  url=self._url,
                                  prompt=self._prompt,
                                  content=self._make_content(question))

        self._logger.debug(f"Successfully created request for question "
                          f"{question.get_qid()}")
        return request

    def _make_content(self, question: Question) -> List[Dict[str, str]]:
        if question.has_img():
            self._logger.debug(f"Processing question with image: "
                              f"{question.get_img_path()}")
            output = [{"type": "image",
                       "image": self._format_image(question.get_img_path())},
                      {"type": "text",
                      "text": self._format_text(question)}]
        else:
            self._logger.debug("Processing text-only question")
            output=[{"type": "text", "text": self._format_text(question)}]
        self._logger.debug(f"Successfully formatted content for question "
                          f"{question.get_qid()}")
        return output

    def _format_text(self, question: Question) -> str:
        """
        Format the question text into a string representation.

        :param question: Question object to format.
        :return: Formatted question text.
        """
        self._logger.debug("Formatting question text")
        return str(self._question_to_dict(question))


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

    def _question_to_dict(self, question: Question) -> Dict[str, str]:
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
            error_msg = (f"Failed to convert question {question.get_qid()}: "
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
        return lettered_choices
