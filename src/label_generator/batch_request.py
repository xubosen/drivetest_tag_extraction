from typing import List
from pydantic import BaseModel, Field

from label_generator.labeling_request_interface import LabelingRequest


class LabelingBatchRequest(BaseModel):
    """Pydantic model for a labeling batch request entry."""
    requests: List[LabelingRequest] = (
        Field(default_factory=list, description="List of labeling requests"))

    def to_batch_jsonl(self) -> str:
        """
        Convert the LabelingBatchRequest to a formatted JSONL string for the
        batch request.
        """
        json_lines = [request.to_request() for request in self.requests]
        return "\n".join(json_lines)

    def to_jsonl_file(self, file_path: str) -> None:
        """
        Save the LabelingBatchRequest to a JSONL file.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.to_batch_jsonl())
        except Exception as e:
            raise IOError(f"Failed to write to file {file_path}: {e}")

    class Config:
        """Pydantic configuration for the LabelingBatchRequest."""
        validate_assignment = True
        extra = "forbid"
        arbitrary_types_allowed = True
