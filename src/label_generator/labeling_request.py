import json
from typing import List, Dict
from pydantic import BaseModel, Field, field_validator

class LabelingRequest(BaseModel):
    custom_id: str = Field(..., min_length=1)
    _method: str = "POST"
    _url: str = "/v1/chat/completions"
    model: str = Field(..., min_length=1,
                       description="Model to use for the request")
    prompt: str = Field(..., min_length=1,
                        description="System _prompt for the model")
    content: List[Dict[str, str]] = Field(..., min_length=1,
                                          description="List of messages")

    @field_validator(mode='after')
    @classmethod
    def validate_content(cls, inputs: List[Dict[str, str]]) \
            -> List[Dict[str, str]]:
        for input in inputs:
            if len(input) != 2:
                raise ValueError("Each content item must have exactly two keys:"
                                 "'type' and the corresponding content key")
            if "type" not in input.keys():
                raise ValueError("Each content item must have a 'type' key")
            if input["type"] not in {"text", "image"}:
                raise ValueError("Content type must be either 'text' or "
                                 "'image'")
            if input["type"] not in input.keys():
                raise ValueError(f"Content item of type '{input['type']}' "
                                 "must have a corresponding key")
        return inputs

    def __str__(self) -> str:
        """
        Return a string representation of the LabelingRequest
        """
        return self.to_request()

    def to_request(self) -> str:
        """
        Convert the LabelingRequest to a formatted JSONL string for the request
        """
        json_dict = {
            "custom_id": self.custom_id,
            "method": self._method,
            "url": self._url,
            "body": {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.content}
                ]
            }
        }
        return json.dumps(json_dict, ensure_ascii=False, indent=0)

class Config:
    validate_assignment = True
    extra = False
    underscore_attrs_are_private = True
