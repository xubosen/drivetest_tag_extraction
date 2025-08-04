from pydantic import (BaseModel,
                      ConfigDict,
                      Field,
                      field_validator,
                      model_validator)
from typing import List, Dict


class Usage(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    completion_tokens: int = Field(ge=0,
                                   description="Number of completion tokens")
    prompt_tokens: int = Field(ge=0,
                               description="Number of prompt tokens")
    completion_tokens_details: Dict[str, int] = (
        Field(description="Completion token details"))
    prompt_tokens_details: Dict[str, int] = (
        Field(description="Prompt token details"))
    total_tokens: int = Field(ge=0,
                              description="Total number of tokens")

    @field_validator('completion_tokens_details',
                     'prompt_tokens_details')
    @classmethod
    def validate_token_details(cls, v):
        for key, value in v.items():
            if value < 0:
                raise ValueError(f"Token detail "
                                 f"'{key}' must be a non-negative integer")
        return v

    @model_validator(mode='after')
    def validate_total_tokens(self):
        if self.total_tokens != self.completion_tokens + self.prompt_tokens:
            raise ValueError("Total tokens must equal completion_tokens "
                             "+ prompt_tokens")
        return self


class Message(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    role: str = Field(..., description="Message role")
    content: str = Field(min_length=1, description="Message content")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v != "assistant":
            raise ValueError("Role must be 'assistant'")
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("Content cannot be empty or only whitespace")
        return v


class Choice(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    finish_reason: str = (
        Field(min_length=1, description="Reason for completion"))
    index: int = Field(ge=0, description="Choice index")
    message: Message = Field(description="Response message")


class ResponseBody(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    created: int = Field(gt=0, description="Creation timestamp")
    usage: Usage = Field(description="Token usage information")
    model: str = Field(min_length=1, description="Model name")
    id: str = Field(min_length=1, description="Response ID")
    choices: List[Choice] = Field(min_length=1,
                                  description="Response choices")
    object: str = Field(..., description="Object type")

    @field_validator('choices')
    @classmethod
    def validate_choices(cls, v):
        if not v:
            raise ValueError("Choices list cannot be empty")
        # Validate indices are sequential starting from 0
        expected_indices = list(range(len(v)))
        actual_indices = [choice.index for choice in v]
        if actual_indices != expected_indices:
            raise ValueError("Choice indices must be sequential starting "
                             "from 0")
        return v


class ResponseData(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    status_code: int = Field(ge=200, le=599, description="HTTP status code")
    request_id: str = Field(min_length=1, description="Request ID")
    response_body: ResponseBody = Field(description="Response body")


class Response(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    response_id: str = Field(min_length=1, description="Response ID")
    custom_id: str = Field(min_length=1, description="Custom ID")
    response_data: ResponseData = Field(description="Response data")

    @model_validator(mode='after')
    def validate_response_consistency(self):
        # Ensure response ID matches body ID
        if self.response_data.response_body.id != f"chatcmpl-{self.response_id}":
            raise ValueError("Response ID must match body ID")

        # If status code indicates error, error field should be present
        if self.response_data.status_code >= 400 and self.error is None:
            raise ValueError("Error field must be present when status code"
                             " indicates error")

        return self

