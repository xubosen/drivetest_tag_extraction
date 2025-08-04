import json
from typing import Dict, List

from entities.question_bank import QuestionBank
from label_generator.response_object import Response
from label_generator.response_factory import ResponseFactory
from label_generator.label_factory import LabelFactory, MessageFormatConfig
from label_generator.label_data import LabelData


class ResponseParsingPipeline:
    _qb: QuestionBank
    _result_path: str
    _msg_format: MessageFormatConfig

    def __init__(self, question_bank: QuestionBank, result_path: str,
                 message_format: MessageFormatConfig):
        self._qb = question_bank
        self._result_path = result_path
        self._msg_format = message_format

    def parse_and_load(self):
        """
        Parse the response data and load it into the question bank.
        """
        response_lst = self._json_to_response()
        qid_to_labels = self._response_to_labels(response_lst)
        self._load_question_bank(qid_to_labels)

    def _json_to_response(self) -> List[Response]:
        """
        Parse the results from the loaded JSON data into a list of Response
        objects.
        """
        response_lst = []
        with open(self._result_path, 'r') as jsonl_file:
            for line in jsonl_file:
                json_response = json.loads(line)
                response = ResponseFactory.create_response(json_response)
                response_lst.append(response)
        return response_lst

    def _response_to_labels(self, response_lst: List[Response]) \
            -> Dict[str, LabelData]:
        """
        Convert a list of Response objects into a dictionary of labels.
        """
        qid_to_labels = {}
        for response in response_lst:
            qid = response.custom_id
            choices = response.response_data.response_body.choices
            for choice in choices:
                message = choice.message
                label_factory = LabelFactory(
                    message_format=self._msg_format)
                label_data = label_factory.make_label_data(message)
                if qid not in qid_to_labels:
                    qid_to_labels[qid] = label_data
                else:
                    qid_to_labels[qid].extend(label_data)
        return qid_to_labels

    def _load_question_bank(self, qid_to_labels: Dict[str, LabelData]):
        """
        Load the labels into the question bank.
        """
        for qid in qid_to_labels.keys():
            question = self._qb.get_question(qid)
            label_data = qid_to_labels[qid]
            question.set_tags(label_data.get_tags())
            question.set_keywords(label_data.get_keywords())
