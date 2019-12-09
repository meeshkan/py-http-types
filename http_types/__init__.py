from typing_extensions import Literal, TypedDict


class Request(TypedDict, total=True):
    method: Literal['get', 'put', 'post', 'patch',
                    'delete', 'options', 'trace', 'head', 'connect']


class Response(TypedDict, total=True):
    code: int
