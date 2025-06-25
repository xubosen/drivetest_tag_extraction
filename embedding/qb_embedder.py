import numpy as np
from transformers import AutoModel
from logging import Logger

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


class QBEmbedder:
    """
    Custom embedder that uses a multimodal model to encode a question bank.
    """
    _model: AutoModel
    _logger: Logger

    def __init__(self, model: AutoModel, logger: Logger):
        """
        Initialize the embedder with a multimodal model from Hugging Face that
        understands mandarin chinese (zho).

        Representational Invariant:
        - model: An instance of a multimodal and multilingual model from
        Hugging Face.
        """
        self._model = model
        self._logger = logger

    def encode_qb(self, qb: QuestionBank) -> np.ndarray:
        """
        Encode the question bank into a single vector space and return the
        embeddings.

        Representation Invariant:
        - qb is not empty
        """
        self._logger.info("Encoding question bank.")
        # Initialize embeddings after encoding the first question
        embeddings = None
        # Counter for tracking our position in the array
        idx = 0

        for chapter_id in qb.get_all_chapter_num():
            self._logger.info(f"Encoding Chapter {chapter_id}")
            for qid in qb.get_qids_by_chapter(chapter_id):
                question = qb.get_question(qid)
                chapter = qb.describe_chapter(chapter_id)
                embedding = self._encode_question(question, chapter)

                # Initialize our embedding array on the first iteration
                if embeddings is None:
                    embeddings = self._make_array(embedding, qb)
                # Store the embedding in the embeddings variable
                self._logger.info(f"Saving embeddings for question {qid} ")
                embeddings[idx] = embedding
                idx += 1

        # Return the encoded questions
        self._logger.info("Finished encoding question bank.")
        return embeddings

    def _make_array(self, embedding, qb):
        embedding_dim = embedding.shape[0]
        self._logger.info(f"Creating embeddings array with "
                          f"dimensions ({qb.question_count()}, "
                          f"{embedding_dim})")
        return np.zeros((qb.question_count(), embedding_dim))

    def _encode_question(self, q: Question, chapter: str) -> np.ndarray:
        """
        Encode a question into a vector space.
        """
        self._logger.info(f"Encoding Question {q.get_qid()}")
        doc = _format_question(q, chapter)
        if _has_image(q):
            image_path = q.get_img_path()
            embedding = self._encode_text_and_img(doc, image_path)
        else:
            embedding = self._encode_text(doc)
        self._logger.info(f"Completed encoding for Question {q.get_qid()}")
        return embedding

    def _encode_text_and_img(self, doc: str, image_path: str) -> np.ndarray:
        """
        Encode both text and image into a vector space.
        """
        text_embedding = self._encode_text(doc)
        image_embedding = self._encode_image(image_path)
        # Average the text and image embeddings
        return (text_embedding + image_embedding) / 2.0

    def _encode_text(self, doc: str) -> np.ndarray:
        """
        Encode question text.
        """
        pass

    def _encode_image(self, image_path: str) -> np.ndarray:
        """
        Encode an image given its image path.
        """
        pass
