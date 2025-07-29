from typing import Dict, Any, List

from label_generator.response_object import (Response,
                                             ResponseData,
                                             ResponseBody,
                                             Choice,
                                             Usage,
                                             Message)


class ResponseFactory:

    @staticmethod
    def create_response(response_json: Dict[Any]) -> Response:
        """
        Create a Response object from a JSON-style dictionary.

        :param response_json: JSON dictionary representing the response data.
        :return: Response object.

        ========== Representational Invariant ==========
        - response_json must contain all required fields as defined in the
          Response model.
        """
        message = Message(role=response_json['response']['body']['choices'][0]
        ['message']['role'],
                          content=response_json['response']['body']['choices']
                          [0]['message']['content'])

        usage = Usage(
            prompt_tokens=response_json['response']['body']['usage']
            ['prompt_tokens'],
            completion_tokens=response_json['response']['body']['usage']
            ['completion_tokens'],
            total_tokens=response_json['response']['body']['usage']
            ['total_tokens'],
            prompt_tokens_details=response_json['response']['body']['usage']
            ['prompt_tokens_details'],
            completion_tokens_details=response_json['response']['body']
            ['usage']['completion_tokens_details']
        )

        choice = Choice(
            finish_reason=response_json['response']['body']['choices']
            [0]['finish_reason'],
            index=response_json['response']['body']['choices'][0]['index'],
            message=message
        )

        body = ResponseBody(
            created=response_json['response']['body']['created'],
            usage=usage,
            model=response_json['response']['body']['model'],
            id=response_json['response']['body']['id'],
            choices=[choice],
            object=response_json['response']['body']['object']
        )

        response_data = ResponseData(
            status_code=response_json['response']['status_code'],
            request_id=response_json['response']['request_id'],
            response_body=body)

        response = Response(response_id=response_json['response']['id'],
                            custom_id=response_json['response']['custom_id'],
                            response_data=response_data)
        return response

    @staticmethod
    def batch_create_response(response_json_list: List[Dict[Any]]) -> (
            Dict)[str, Response]:
        """
        Create a batch of Response objects from a list of JSON-style
        dictionaries.
        """
        result = {}
        for response_json in response_json_list:
            response = ResponseFactory.create_response(response_json)
            result[response.response_id] = response
        return result

