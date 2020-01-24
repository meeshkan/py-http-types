from http_types.utils import RequestBuilder
from os import path
import os
import json
from http_types import HttpExchange, HttpExchangeBuilder
from typeguard import check_type  # type: ignore

dir_path = os.path.dirname(os.path.realpath(__file__))
SAMPLE_JSON = path.join(dir_path, "resources", "sample.json")
SAMPLE_JSONL = path.join(dir_path, "resources", "sample.jsonl")


def read_example():
    with open(SAMPLE_JSON) as f:
        content = f.read()
        return json.loads(content)


request_response_pair = read_example()


def test_typeguard():
    reqres = HttpExchangeBuilder.from_dict(request_response_pair)
    check_type("reqres", reqres, HttpExchange)


def test_request_from_dict():
    dict_req = {
        'host': 'api.github.com',
        'protocol': 'https',
        'method': 'get',
        'path': '/v1/users',
        'query': {}
    }
    req = RequestBuilder.from_dict(dict_req)
    assert req['method'] == "get"
    assert req['host'] == "api.github.com"
    assert req['protocol'] == "https"
    assert req['body'] == ''
    assert req['headers'] == {}


def test_from_url():
    test_url = "https://api.github.com/v1/repos?id=1"
    req = RequestBuilder.from_url(test_url)
    assert req['method'] == "get"
    assert req['host'] == "api.github.com"
    assert req['protocol'] == "https"
    assert req['path'] == "/v1/repos?id=1"
    assert req['pathname'] == "/v1/repos"
    assert req['query'] == {'id': ['1']}

def test_from_jsonl():
    with open(SAMPLE_JSONL, "r", encoding="utf-8") as f:
        exchanges = list(HttpExchangeBuilder.from_jsonl(f))
        assert exchanges[0]['req']['protocol'] == 'http'
        assert exchanges[1]['req']['protocol'] == 'https'
