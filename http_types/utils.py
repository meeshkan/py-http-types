import json
from datetime import datetime
from typing import Any, Dict, Generator, IO, Union
from urllib.parse import urlencode, urlparse, parse_qs
from http.client import HTTPResponse
from dateutil.parser import isoparse
import copy
from dataclasses import asdict, is_dataclass
from http_types.types import (
    HttpMethod,
    Protocol,
    HttpExchange,
    Request,
    Response,
    Headers,
    Query,
)
import re
from urllib import request

__all__ = [
    "RequestBuilder",
    "ResponseBuilder",
    "HttpExchangeBuilder",
    "HttpExchangeReader",
    "HttpExchangeWriter",
]


class BuilderException(Exception):
    pass


def parse_body(body: str) -> Any:
    # TODO Handle errors for non-json
    try:
        return json.loads(body)
    except json.JSONDecodeError:
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
    return urlparse(path).path


path_capture = re.compile(r"^https?:\/\/[^\/]+(\/(?:\S)*)?$")


def path_from_url(url: str) -> str:
    """
    Infer path from URL.

    Arguments:
        url {str} -- URL such as https://foo.bar/v1/

    Returns:
        str -- Path portion of the URL
    """
    match_result = path_capture.match(url)
    if match_result is None:
        raise Exception("Unknown format for url {url}".format(url=url))
    groups = match_result.groups()
    if len(groups) == 0 or groups[0] is None:  # Path empty
        return "/"
    else:
        return groups[0]


def parse_qs_flattening(query_string: str) -> Query:
    query_dict: Dict = parse_qs(query_string)
    for (key, values) in query_dict.items():
        if len(values) == 1:
            query_dict[key] = values[0]
    return query_dict


def delete_entries_for_serialization(data_to_be_serialized):
    """Delete entries that are not to be serialized to JSON."""
    result = (
        asdict(data_to_be_serialized)
        if is_dataclass(data_to_be_serialized)
        else copy.deepcopy(data_to_be_serialized)
    )
    to_iter = copy.deepcopy(result)
    for key, value in to_iter.items():
        if key == "bodyAsJson" or value is None or value == "":
            del result[key]
        if key == "method":
            result[key] = result[key].value
        if key == "protocol":
            result[key] = result[key].value
        elif isinstance(value, dict):
            result[key] = delete_entries_for_serialization(value)
    return result


def parse_iso860_datetime(input_string: str) -> datetime:
    try:
        return isoparse(input_string)
    except ValueError:
        # The error message from isoparse() is not informative,
        # so we provide our own:
        raise ValueError("Invalid isoformat string: " + input_string)


def url_encode_params(params: Dict):
    """Wrapper around urlencode() that handles multi-valued (mapped to an array) parameters."""
    params_list = []
    for key, value in params.items():
        if isinstance(value, list):
            params_list.extend([(key, x) for x in value])
        else:
            params_list.append((key, value))
    return urlencode(params_list)


class RequestBuilder:
    def __init__(self):
        raise Exception("Do not instantiate")

    @staticmethod
    def from_urllib_request(obj: request.Request) -> Request:
        parsed = urlparse(obj.full_url)
        req = RequestBuilder.from_dict(dict(
            method=obj.get_method().lower() if obj.get_method() is not None else "get",
            path=parsed.path,
            pathname=parsed.path,
            host=parsed.netloc,
            query=parsed.query,
            protocol='https' if obj.full_url[:5] == 'https' else 'http',
            body=obj.data if isinstance(obj.data , str) else obj.data.decode('utf8') if isinstance(obj.data, bytes) else None,
            headers={ k: v for k, v in obj.header_items() }
        ))
        RequestBuilder.validate(req)
        return req

    @staticmethod
    def from_dict(obj: Dict) -> Request:
        obj_copy = dict(**obj)

        obj_copy["method"] = HttpMethod(obj_copy["method"])
        obj_copy["protocol"] = Protocol(obj_copy["protocol"])

        if (obj_copy.get("path", None) is not None) and (obj_copy.get("query", None) is None):
            query_dict = parse_qs_flattening(urlparse(obj_copy["path"]).query)
            obj_copy["query"] = query_dict

        if obj_copy.get("path", None) is None:
            if "pathname" not in obj_copy:
                raise Exception("One of 'path' or 'pathname' is required")
            path = obj_copy["pathname"]
            if "query" in obj_copy:
                path += "?" + url_encode_params(obj_copy["query"])
            obj_copy["path"] = path

        if obj_copy.get("pathname", None) is None:
            path = obj_copy["path"]
            obj_copy["pathname"] = parse_pathname(path)

        if obj_copy.get("body", None) is None:
            obj_copy["body"] = ""

        if obj_copy.get("headers", None) is None:
            obj_copy["headers"] = {}

        if obj_copy.get("bodyAsJson", None) is None:
            body_as_json = parse_body(obj_copy["body"])
            obj_copy["bodyAsJson"] = body_as_json

        if obj_copy.get("timestamp", None) is None:
            obj_copy["timestamp"] = None
        else:
            obj_copy["timestamp"] = parse_iso860_datetime(obj_copy["timestamp"])

        req = Request(**obj_copy)
        RequestBuilder.validate(req)
        return req

    @staticmethod
    def validate_protocol(proto: str) -> Protocol:
        if proto not in ["http", "https"]:
            raise BuilderException("")
        return Protocol(proto)

    @staticmethod
    def from_url(
        url: str, method: HttpMethod = HttpMethod.GET, headers: Headers = {}
    ) -> Request:
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
        pathname = parsed_url.path or "/"
        path = path_from_url(url)

        # Query string
        query_str = parsed_url.query

        query = parse_qs_flattening(query_str)

        host = parsed_url.netloc

        req = Request(
            method=method,
            protocol=protocol,
            host=host,
            body="",
            bodyAsJson="",
            path=path,
            pathname=pathname,
            query=query,
            headers=headers,
            timestamp=None,
        )
        RequestBuilder.validate(req)
        return req

    @staticmethod
    def validate(request: Request) -> None:
        """Run-time typechecking for request object.

        Arguments:
            request {Request} -- Possible request object.
        """
        # No validation currently needed, safe to remove
        # if no future validation needed
        pass


class ResponseBuilder:
    def __init__(self):
        raise Exception("Do not instantiate")

    @staticmethod
    def from_http_client_response(obj: HTTPResponse) -> Response:
        body = obj.read()
        res = ResponseBuilder.from_dict(dict(
            statusCode=obj.getcode(),
            headers={k:v for k,v in obj.getheaders()},
            body=body if isinstance(body , str) else body.decode('utf8') if isinstance(body, bytes) else None,
        ))
        ResponseBuilder.validate(res)
        return res

    @staticmethod
    def from_dict(obj: Any) -> Response:
        obj_copy = dict(**obj)

        if obj_copy.get("bodyAsJson", None) is None:
            body_as_json = parse_body(obj_copy["body"])
            obj_copy["bodyAsJson"] = body_as_json

        if obj_copy.get("timestamp", None) is None:
            obj_copy["timestamp"] = None
        else:
            obj_copy["timestamp"] = parse_iso860_datetime(obj_copy["timestamp"])

        res = Response(**obj_copy)
        ResponseBuilder.validate(res)
        return res

    @staticmethod
    def validate(response: Response) -> None:
        """Run-time typechecking for response object.

        Arguments:
            response {Response} -- Possible response object.
        """
        pass


class HttpExchangeBuilder:
    """Builder of HttpExchange instances with the from_dict() method."""

    def __init__(self):
        raise Exception("Do not instantiate")

    @staticmethod
    def from_dict(obj: Dict) -> HttpExchange:
        """
        Build HttpExchange from dictionary, filling in any optional fields.

        Arguments:
            obj {Any} -- Dictionary containing at least protocol, hostname, path, and headers.

        Raises:
            BuilderException: For invalid dictionary.

        Returns:
            HttpExchange -- Request-response pair.
        """
        if "request" not in obj:
            raise BuilderException("Missing request")

        if "response" not in obj:
            raise BuilderException("Missing response")

        req_obj = obj["request"]
        req = RequestBuilder.from_dict(req_obj)

        res_obj = obj["response"]
        res = ResponseBuilder.from_dict(res_obj)

        reqres = HttpExchange(request=req, response=res)
        HttpExchangeBuilder.validate(reqres)
        return reqres

    @staticmethod
    def validate(reqres: HttpExchange) -> None:
        """Run-time typechecking for request-response pair.

        Arguments:
            reqres {HttpExchange} -- Possible request-response object.
        """
        pass


class HttpExchangeReader:
    def __init__(self):
        raise Exception("Do not instantiate")

    @staticmethod
    def from_json(input_json: Union[str, bytes]) -> HttpExchange:
        """Read a single HTTP exchange from a JSON string.

        Arguments:
            input_json: {str} -- The input JSON to parse.
        """
        return HttpExchangeBuilder.from_dict(json.loads(input_json))

    @staticmethod
    def from_jsonl(input_file: IO[str]) -> Generator[HttpExchange, None, None]:
        """Read HTTP exchanges line by line from a file-like object.

        Arguments:
            input_file: {IO} -- The input to read from.
        """
        for line in input_file:
            yield HttpExchangeReader.from_json(line)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


class HttpExchangeWriter:
    def __init__(self, output: IO[str]):
        """Create a writer of HTTP exchanges.

        Each exchange will be written as a JSON object in the HTTP types
        format on a single line.

        Arguments:
            output: {IO} -- The output to write to
        """
        self.output = output

    def write(self, exchange: HttpExchange):
        """Write a single HTTP exchange line to the output.

        Arguments:
            exchange: {HttpExchange} -- The exchange to write.
        """
        json.dump(
            delete_entries_for_serialization(exchange), self.output, default=json_serial
        )
        self.output.write("\n")
