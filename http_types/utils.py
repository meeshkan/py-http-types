
from http_types.types import HttpMethod, Protocol, RequestResponsePair, Request, Response, Headers
from typing import Any, cast
from typeguard import check_type  # type: ignore
import json
from urllib.parse import urlparse, parse_qs

__all__ = ["RequestBuilder", "ResponseBuilder", "RequestResponseBuilder"]


class BuilderException(Exception):
    pass


def parse_body(body: str) -> Any:
    # TODO Handle errors for non-json
    try:
        return json.loads(body)
    except:
        # TODO Typeguard does not accept missing arguments so return empty string for now
        return ""


def parse_pathname(path: str) -> str:
    """Parse pathname from path.

    Example: /v1/repos?id=1 => /v1/repos

    Arguments:
        path {str} -- [description]

    Returns:
        str -- [description]
    """
    return path


def path_from_url(url: str) -> str:
    """
    Infer path from URL.

    Arguments:
        url {str} -- URL such as https://foo.bar/v1/

    Returns:
        str -- Path portion of the URL
    """
    splitted = url.split("/", 3)
    if len(splitted) < 3:
        return ""
    return "/" + splitted[3]


class RequestBuilder:
    def __init__(self):
        raise Exception("Do not instantiate")

    @staticmethod
    def from_dict(obj: Any) -> Request:
        obj_copy = dict(**obj)

        if not "pathname" in obj_copy:
            path = obj_copy['path']
            obj_copy['pathname'] = parse_pathname(path)

        if not "body_as_json" in obj_copy:
            body_as_json = parse_body(obj_copy['body'])
            obj_copy['body_as_json'] = body_as_json

        req = Request(**obj_copy)
        RequestBuilder.validate(req)
        return req

    @staticmethod
    def validate_protocol(proto: str) -> Protocol:
        if not proto in ["http", "https"]:
            raise BuilderException("")
        return cast(Protocol, proto)

    @staticmethod
    def from_url(url: str, method: HttpMethod = "get", headers: Headers = {}) -> Request:
        """Parse Request object from url.

        Arguments:
            url {str} -- URL as string.

        Keyword Arguments:
            method {HttpMethod} -- HTTP method. (default: {"get"})

        Returns:
            Request -- Request object.
        """
        # https://docs.python.org/3/library/urllib.parse.html
        parsed_url = urlparse(url)

        protocol = RequestBuilder.validate_protocol(parsed_url.scheme)

        # Path and pathname
        pathname = parsed_url.path
        path = path_from_url(url)

        # Query string
        query_str = parsed_url.query

        # TODO Fix typing, parse_qs seems to return a lists as dictionary values?
        query = parse_qs(query_str)

        host = parsed_url.netloc

        req = Request(method=method,
                      protocol=protocol,
                      host=host,
                      body="",
                      body_as_json="",
                      path=path,
                      pathname=pathname,
                      query=query,
                      headers=headers)
        RequestBuilder.validate(req)
        return req

    @staticmethod
    def validate(request: Request) -> None:
        """Run-time typechecking for request object.

        Arguments:
            request {Request} -- Possible request object.
        """
        check_type("request", request, Request)
        method = request['method']
        # typeguard does not support checking Literal from typing-extensions,
        # so check it by hand
        # https://github.com/agronholm/typeguard/issues/64
        assert method in ['get',
                          'put',
                          'post',
                          'patch',
                          'delete',
                          'options',
                          'trace',
                          'head',
                          'connect']


class ResponseBuilder:
    def __init__(self):
        raise Exception("Do not instantiate")

    @staticmethod
    def from_dict(obj: Any) -> Response:
        obj_copy = dict(**obj)

        if not "body_as_json" in obj_copy:
            body_as_json = parse_body(obj_copy['body'])
            obj_copy['body_as_json'] = body_as_json

        res = Response(**obj_copy)
        ResponseBuilder.validate(res)
        return res

    @staticmethod
    def validate(response: Response) -> None:
        """Run-time typechecking for response object.

        Arguments:
            response {Response} -- Possible response object.
        """
        check_type("response", response, Response)


class RequestResponseBuilder:

    def __init__(self):
        raise Exception("Do not instantiate")

    @staticmethod
    def from_dict(obj: Any) -> RequestResponsePair:
        """
        Build RequestResponsePair from dictionary, filling in any optional fields.

        Arguments:
            obj {Any} -- Dictionary containing at least protocol, hostname, path, and headers.

        Raises:
            BuilderException: For invalid dictionary.

        Returns:
            RequestResponsePair -- Request-response pair.
        """
        if not 'req' in obj:
            raise BuilderException("Missing req")

        if not 'res' in obj:
            raise BuilderException("Missing res")

        req_obj = obj['req']
        req = RequestBuilder.from_dict(req_obj)

        res_obj = obj['res']
        res = ResponseBuilder.from_dict(res_obj)

        reqres = RequestResponsePair(req=req, res=res)
        RequestResponseBuilder.validate(reqres)
        return reqres

    @staticmethod
    def validate(reqres: RequestResponsePair) -> None:
        """Run-time typechecking for request-response pair.

        Arguments:
            reqres {RequestResponsePair} -- Possible request-response object.
        """
        check_type("request-response", reqres, RequestResponsePair)
