
from datetime import datetime
from http_types.types import HttpMethod, Protocol, HttpExchange, Request, Response, Headers, Query
from typing import Any, cast, Dict, Generator, IO, Union
import json
from urllib.parse import urlencode, urlparse, parse_qs
from backports.datetime_fromisoformat import MonkeyPatch

__all__ = ["RequestBuilder", "ResponseBuilder", "HttpExchangeBuilder", "HttpExchangeReader", "HttpExchangeWriter"]

MonkeyPatch.patch_fromisoformat()

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
    return urlparse(path).path


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


def parse_qs_flattening(query_string: str) -> Query:
    query_dict: Dict = parse_qs(query_string)
    for (key, values) in query_dict.items():
        if len(values) == 1:
            query_dict[key] = values[0]
    return query_dict


def delete_none_entries(d):
    result = d.copy()
    for key, value in d.items():
        if value is None or value == '':
            del result[key]
        elif isinstance(value, dict):
            result[key] = delete_none_entries(value)
    return result


class RequestBuilder:
    def __init__(self):
        raise Exception("Do not instantiate")

    @staticmethod
    def from_dict(obj: Dict) -> Request:
        obj_copy = dict(**obj)

        if not "query" in obj_copy and "path" in obj_copy:
            query_dict = parse_qs_flattening(urlparse(obj_copy["path"]).query)
            obj_copy['query'] = query_dict

        if not "path" in obj_copy:
            if not "pathname" in obj_copy:
                raise Exception("One of 'path' or 'pathname' is required")
            path = obj_copy["pathname"]
            if "query" in obj_copy:
                path += "?" + urlencode(obj_copy["query"])
            obj_copy['path'] = path

        if not "pathname" in obj_copy:
            path = obj_copy['path']
            obj_copy['pathname'] = parse_pathname(path)

        if not "body" in obj_copy:
            obj_copy['body'] = ""

        if not "headers" in obj_copy:
            obj_copy['headers'] = {}

        if not "bodyAsJson" in obj_copy:
            body_as_json = parse_body(obj_copy['body'])
            obj_copy['bodyAsJson'] = body_as_json

        if "timestamp" in obj_copy:
            obj_copy['timestamp'] = datetime.fromisoformat(obj_copy['timestamp'])

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

        query = parse_qs_flattening(query_str)

        host = parsed_url.netloc

        req = Request(method=method,
                      protocol=protocol,
                      host=host,
                      body="",
                      bodyAsJson="",
                      path=path,
                      pathname=pathname,
                      query=query,
                      headers=headers,
                      timestamp=None)
        RequestBuilder.validate(req)
        return req

    @staticmethod
    def validate(request: Request) -> None:
        """Run-time typechecking for request object.

        Arguments:
            request {Request} -- Possible request object.
        """
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

        if not "bodyAsJson" in obj_copy:
            body_as_json = parse_body(obj_copy['body'])
            obj_copy['bodyAsJson'] = body_as_json

        if "timestamp" in obj_copy:
            obj_copy['timestamp'] = datetime.fromisoformat(obj_copy['timestamp'])

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

    def __init__(self):
        raise Exception("Do not instantiate")

    @staticmethod
    def from_dict(obj: Any) -> HttpExchange:
        """
        Build HttpExchange from dictionary, filling in any optional fields.

        Arguments:
            obj {Any} -- Dictionary containing at least protocol, hostname, path, and headers.

        Raises:
            BuilderException: For invalid dictionary.

        Returns:
            HttpExchange -- Request-response pair.
        """
        if not 'request' in obj:
            raise BuilderException("Missing request")

        if not 'response' in obj:
            raise BuilderException("Missing response")

        req_obj = obj['request']
        req = RequestBuilder.from_dict(req_obj)

        res_obj = obj['response']
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
    raise TypeError ("Type %s not serializable" % type(obj))


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
        json.dump(delete_none_entries(exchange), self.output, default=json_serial)
        self.output.write("\n")
