from datetime import datetime
from typing_extensions import Literal, TypedDict
from typing import Any, Union, Mapping, Sequence

"""
HTTP request or response headers. Array-valued header values can be represented with a comma-separated string.
"""
Headers = Mapping[str, Union[str, Sequence[str]]]

"""
HTTP request query parameters.
"""
Query = Mapping[str, Union[str, Sequence[str]]]

"""
HTTP request protocol.
"""
Protocol = Literal['http', 'https']

"""
HTTP method.
"""
HttpMethod = Literal['get',
                     'put',
                     'post',
                     'patch',
                     'delete',
                     'options',
                     'trace',
                     'head',
                     'connect']


class _Request(TypedDict, total=False):
    """
    Optional fields for Request.
    """

    """
    HTTP request body as JSON. Could be dictionary, list, or string.
    """
    bodyAsJson: Any

    """
    Timestamp when the request was initiated.
    """
    timestamp: datetime


class Request(_Request, total=True):
    """
    HTTP request.
    """

    """
    Request method.
    """
    method: HttpMethod

    """
    Request headers.
    """
    headers: Headers

    """
    Query parameters.
    """
    query: Query

    """
    Request body. Empty string if empty.
    """
    body: str

    """
    Request host, possibly including port number.
    """
    host: str

    """
    Full request path.
    Example value: '/v1/pets?id=234'
    """
    path: str

    """
    Request pathname, not containing query parameters etc.
    Example value: '/v1/pets'
    """
    pathname: str

    """
    Request protocol.
    """
    protocol: Protocol


class _Response(TypedDict, total=False):
    """
    Optional fields for Response.
    """

    """
    Response body as JSON. Could be dictionary, list, or string.
    """
    bodyAsJson: Any

    """
    Timestamp when the response was sent.
    """
    timestamp: datetime


class Response(_Response, total=True):
    """
    HTTP response.
    """

    """
    Response body.
    """
    body: str

    """ Response status code."""
    statusCode: int

    """ Response headers. """
    headers: Headers


class HttpExchange(TypedDict, total=True):
    """
    HTTP request-response pair.
    """
    request: Request
    response: Response


__all__ = ["Request", "Response", "HttpExchange",
           "Headers", "Query", "Protocol", "HttpMethod"]
