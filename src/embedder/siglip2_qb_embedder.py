import numpy as np
from transformers.models.siglip2.modeling_siglip2 import Siglip2Model
from transformers.models.siglip2.processing_siglip2 import Siglip2Processor
from logging import Logger
from typing import Dict
from torch.nn.functional import normalize
from torch import Tensor
from PIL import Image

from qb.question import Question
from qb.question_bank import QuestionBank


def _has_image(q: Question) -> bool:
    """
    Check if the question contains an image.
    """
    return q.get_img_path() is not None


def _format_question(q: Question, chapter: str) -> str:
    """
    Format the question into a string suitable for encoding.
    """
    return f"章节: {chapter}\n题目: {q.get_question()}\n" \
           f"答案: {q.get_correct_answer()}"


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
        # Pre-create dummy image to avoid repeated creation
        self._dummy_image = self._create_dummy_image()
        # Set max length based on model's position embeddings limit
        # Using 60 to leave some buffer for special tokens
        self._max_length = 60

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
            for qid in qb.get_qids_by_chapter(chapter_id):
                question = qb.get_question(qid)
                chapter = qb.describe_chapter(chapter_id)
                embedding = self._encode_question(question, chapter)
                embeddings[qid] = embedding

        # Return the encoded questions
        self._logger.info("Finished encoding question bank.")
        return embeddings

    def _encode_question(self, q: Question, chapter: str) -> np.ndarray:
        """
        Encode a question into a vector space.
        """
        self._logger.info(f"Encoding Question {q.get_qid()}")
        doc = _format_question(q, chapter)
        if _has_image(q):
            image_path = q.get_img_path()
            tensor_embedding = self._encode_text_and_img(doc, image_path)
        else:
            tensor_embedding = self._encode_text(doc)
        np_embedding = tensor_embedding.squeeze().detach().numpy()
        self._logger.info(f"Completed encoding for Question {q.get_qid()}")
        return np_embedding

    def _encode_text_and_img(self, doc: str, image_path: str) -> Tensor:
        """
        Encode both text and image into a vector space.
        """
        self._logger.info("Encoding text and image.")
        with open(image_path, 'rb') as img_file:
            img = Image.open(img_file)
        inputs = self._processor(text=doc, images=img, return_tensors="pt",
                                 padding=True, truncation=True,
                                 max_length=self._max_length)
        outputs = self._model(**inputs)
        # Average the text and image embeddings
        combined_embedding = (outputs.text_embeds + outputs.image_embeds) / 2.0
        # Normalize the combined embedding
        return normalize(combined_embedding, p=2, dim=-1)

    def _encode_text(self, doc: str) -> Tensor:
        """
        Encode question text using dummy image for a multimodal model.
        """
        self._logger.info("Encoding text only with dummy image.")

        inputs = self._processor(
            text=doc,
            images=self._dummy_image,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self._max_length
        )

        outputs = self._model(**inputs)
        return outputs.text_embeds

    def _create_dummy_image(self) -> Image.Image:
        """
        Create a dummy image for cases where no image is provided.
        Returns a consistent dummy image that won't cause processing issues.
        """
        self._logger.debug("Creating dummy image for text-only encoding.")
        # Create a small but valid RGB image
        return Image.new('RGB', (256, 256), color=(255, 255, 255))
