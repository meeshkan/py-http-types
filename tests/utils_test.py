from http_types.utils import RequestBuilder
from os import path
import os
import json
from http_types import RequestResponsePair, RequestResponseBuilder
from typeguard import check_type  # type: ignore

dir_path = os.path.dirname(os.path.realpath(__file__))
SAMPLE_JSON = path.join(dir_path, "resources", "sample.json")


def read_example():
    with open(SAMPLE_JSON) as f:
        content = f.read()
        return json.loads(content)


request_response_pair = read_example()


def test_typeguard():
    reqres = RequestResponseBuilder.from_dict(request_response_pair)
    check_type("reqres", reqres, RequestResponsePair)


def test_from_url():
    test_url = "https://api.github.com/v1/repos?id=1"
    req = RequestBuilder.from_url(test_url)
    assert req['method'] == "get"
    assert req['host'] == "api.github.com"
    assert req['protocol'] == "https"
    assert req['path'] == "/v1/repos?id=1"
    assert req['pathname'] == "/v1/repos"
    assert req['query'] == {'id': ['1']}
