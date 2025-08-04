from abc import ABC, abstractmethod
from typing import List, Dict


class LabelingRequest(ABC):
    """
    Abstract base class for labeling requests.
    """
    custom_id: str
    url: str
    model: str
    prompt: str
    content: List[Dict[str, str]]

    @abstractmethod
    def to_request(self) -> str:
        """
        Convert the BasicLabelingRequest to a formatted JSONL string for the
        request.
        """
        raise NotImplementedError("Subclasses must implement this method")
