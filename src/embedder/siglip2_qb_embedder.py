"""Class that encodes a QuestionBank using the Siglip2 multimodal model."""

# Library Imports
from logging import Logger
import numpy as np
from PIL import Image
from torch import Tensor
from torch.nn.functional import normalize
from transformers.models.siglip2.modeling_siglip2 import Siglip2Model
from transformers.models.siglip2.processing_siglip2 import Siglip2Processor
from typing import Dict

# Module Imports
from qb.question import Question
from qb.question_bank import QuestionBank

# Constants
MAX_LENGTH = 64
DUMMY_IMG = Image.new(mode='RGB', size=(256, 256), color=(127, 127, 127))


def format_question(q: Question, chapter: str,
                    include_chapter: bool = False) -> str:
    """
    Format the question into a string suitable for encoding.
    """
    if include_chapter:
        text = (f"章节:{chapter}"
                f"题目:{q.get_question()}"
                f"答案:{q.get_correct_answer()}")
    else:
        text = (f"题目:{q.get_question()}"
                f"答案:{q.get_correct_answer()}")
    return text


class Siglip2QBEmbedder:
    """
    Custom embedder that uses a multimodal model to encode a question bank.
    """
    _model: Siglip2Model
    _processor: Siglip2Processor
    _logger: Logger
    _dummy_image: Image.Image
    _max_length: int

    def __init__(self, model: Siglip2Model, processor: Siglip2Processor,
                 logger: Logger):
        """
        Initialize the embedder with a multimodal model from Hugging Face that
        understands mandarin chinese (zho).

        Representational Invariant:
        - model and processor come from valid multimodal and multilingual models
         from Hugging Face
        """
        self._model = model
        self._processor = processor
        self._logger = logger
        self._dummy_image = DUMMY_IMG
        self._max_length = MAX_LENGTH

    def encode_qb(self, qb: QuestionBank) -> Dict[str, np.ndarray]:
        """
        Encode the question bank into a single vector space and return the
        embeddings as a dictionary mapping question IDs to their embeddings.

        Representation Invariant:
        - qb is not empty
        """
        self._logger.info("Encoding question bank.")

        embeddings = {}
        for chapter_id in qb.get_all_chapter_num():
            self._logger.info(f"Encoding Chapter {chapter_id}")
            for id in qb.get_qids_by_chapter(chapter_id):
                embeddings[id] = self._encode_q(qb.get_question(id),
                                                qb.describe_chapter(chapter_id))

        self._logger.info("Finished encoding question bank.")
        return embeddings

    def _encode_q(self, questn: Question, chapter: str) -> np.ndarray:
        """
        Encode a question into a vector space.
        """
        self._logger.debug(f"Encoding Question {questn.get_qid()}")

        has_image = questn.get_img_path() is not None
        raw_output = self._encode_helper(format_question(questn, chapter),
                                         self._load_image(questn),
                                         has_image)
        tensor_embeddings = normalize(raw_output, p=2, dim=1)
        np_embeddings = tensor_embeddings.squeeze().detach().numpy()

        self._logger.debug(f"Completed encoding for "
                           f"Question {questn.get_qid()}\n"
                           f"Sample: {np_embeddings[:5]}... \n"
                           f"Shape: {np_embeddings.shape}"
                           )
        return np_embeddings

    def _load_image(self, question: Question) -> Image.Image:
        if question.get_img_path() is not None:
            with open(question.get_img_path(), 'rb') as img_file:
                img = Image.open(img_file)
        else:
            img = self._dummy_image
        return img

    def _encode_helper(self, doc: str, img: Image.Image, has_img: bool) -> Tensor:
        inputs = self._processor(text=doc,
                                 images=img,
                                 return_tensors="pt",
                                 padding="max_length",
                                 truncation=True,
                                 max_length=self._max_length)
        outputs = self._model(**inputs)

        if has_img:
            return (outputs.text_embeds + outputs.image_embeds) / 2.0
        else:
            return outputs.text_embeds
