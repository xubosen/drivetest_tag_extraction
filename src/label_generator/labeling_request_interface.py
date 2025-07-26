from abc import ABC, abstractmethod


class LabelingRequest(ABC):
    """
    Abstract base class for labeling requests.
    """

    @abstractmethod
    def to_request(self) -> str:
        """
        Convert the BasicLabelingRequest to a formatted JSONL string for the
        request.
        """
        raise NotImplementedError("Subclasses must implement this method")
