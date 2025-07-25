from logging import Logger

from entities.question_bank import QuestionBank
from label_generator.batch_request import LabelingBatchRequest
from label_generator.request_factory import RequestFactory


class BatchRequestFactory:
    """
    A Pydantic model to format the question bank into a batch request object
    specified by the OpenAI API for batch processing.
    """
    _qb: QuestionBank
    _url: str
    _model: str
    _prompt: str
    _request_factory: RequestFactory
    _logger: Logger

    def __init__(self, question_bank: QuestionBank, url: str, model_name: str,
                 prompt: str, logger: Logger):
        self._qb = question_bank
        self._url = url
        self._model = model_name
        self._prompt = prompt
        self._request_factory = RequestFactory(model=model_name, url=url,
                                               prompt=prompt, logger=logger)
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
            question = self._qb.get_question(qid)
            labeling_request = self._request_factory.make_request(
                question=question, custom_id=qid)
            requests_lst.append(labeling_request)

            if processed_count % 100 == 0:
                self._logger.info(f"Processed {processed_count}/"
                                 f"{self._qb.question_count()} questions")

        batch_request = LabelingBatchRequest(requests=requests_lst)

        self._logger.info(f"Successfully created batch request.")
        return batch_request
