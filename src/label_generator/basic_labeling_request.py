import json
from typing import List, Dict
from pydantic import BaseModel, ConfigDict, Field, field_validator, \
    model_validator

from label_generator.labeling_request_interface import LabelingRequest

REQUEST_METHOD_FIELD = "POST"
URL_TO_MODELS = {
    "/v1/chat/ds-test": {"batch-test-model"},
    "/v1/chat/completions": {'deepseek-r1',
                             'deepseek-v3',
                             'qwen-long',
                             'qwen-long-latest',
                             'qwen-max',
                             'qwen-max-latest',
                             'qwen-plus',
                             'qwen-plus-latest',
                             'qwen-turbo',
                             'qwen-turbo-latest',
                             'qwq-32b-preview',
                             'qwq-plus',
                             'qwen-vl-max',
                             'qwen-vl-max-latest',
                             'qwen-vl-plus'
                             'qwen-omni-turbo'},
    "/v1/embeddings": {"text-embedding-v1",
                       "text-embedding-v2",
                       "text-embedding-v3",
                       "text-embedding-v4"}
}


class BasicLabelingRequest(BaseModel, LabelingRequest):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )
    custom_id: str = Field(..., min_length=1)
    url: str = Field(..., description="URL for the request")
    model: str = Field(..., min_length=1,
                       description="Model to use for the request")
    prompt: str = Field(..., min_length=1,
                        description="System _prompt for the model")
    content: List[Dict[str, str]] = Field(..., min_length=1,
                                          description="List of messages")

    @field_validator("url")
    @classmethod
    def validate_url(cls, url: str) -> str:
        if url not in URL_TO_MODELS.keys():
            raise ValueError(f"URL must be one of {URL_TO_MODELS.keys()}")
        return url

    @field_validator("content")
    @classmethod
    def validate_content(cls, content: List[Dict[str, str]]) \
            -> List[Dict[str, str]]:
        for message in content:
            if len(message) != 2:
                raise ValueError("Each content item must have exactly two keys:"
                                 "'type' and the corresponding content key")
            if "type" not in message.keys():
                raise ValueError("Each content item must have a 'type' key")
            if message["type"] not in {"text", "image_url"}:
                raise ValueError("Content type must be either 'text' or "
                                 "'image_url'")
            if message["type"] not in ["text", "image_url"]:
                raise ValueError(f"Content item of type '{message['type']}' "
                                 f"must have a corresponding key in"
                                 f" {['text', 'image_url']}")
        return content

    @model_validator(mode='after')
    def validate_model_match_url(self):
        """ Check that the model matches the url. """
        if self.model not in URL_TO_MODELS[self.url]:
            raise ValueError(f"Model '{self.model}' is not valid for URL "
                             f"'{self.url}'. Valid models are: "
                             f"{URL_TO_MODELS[self.url]}")
        return self

    def __str__(self) -> str:
        """
        Return a string representation of the BasicLabelingRequest
        """
        return self.to_request()

    def to_request(self) -> str:
        """
        Convert the BasicLabelingRequest to a formatted JSONL string for the
        request
        """
        json_dict = {
            "custom_id": self.custom_id,
            "method": REQUEST_METHOD_FIELD,
            "url": self.url,
            "body": {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.content}
                ]
            }
        }
        return json.dumps(json_dict, ensure_ascii=False)
