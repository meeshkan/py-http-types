from http_types.utils import RequestBuilder
from datetime import datetime
from io import StringIO
from os import path
import os
import json
from http_types import HttpExchange, HttpExchangeBuilder, HttpExchangeReader, HttpExchangeWriter
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
    test_url = "https://api.github.com/v1/repos?id=1&q=v1&q=v2"
    req = RequestBuilder.from_url(test_url)
    assert req['method'] == "get"
    assert req['host'] == "api.github.com"
    assert req['protocol'] == "https"
    assert req['path'] == "/v1/repos?id=1&q=v1&q=v2"
    assert req['pathname'] == "/v1/repos"
    assert req['query'] == {'id': "1", 'q': ["v1", "v2"]}


def test_from_json():
    with open(SAMPLE_JSON, "r", encoding="utf-8") as f:
        exchange = HttpExchangeReader.from_json(f.read())
        assert exchange['request']['timestamp'] == datetime.fromisoformat("2018-11-13T20:20:39+02:00")
        assert exchange['response']['timestamp'] == datetime.fromisoformat("2020-01-31T13:34:15")


def test_invalid_timestamp_in_json():
    with open(SAMPLE_JSON, "r", encoding="utf-8") as f:
        json_string = f.read().replace("2018-11-13T20:20:39+02:00", "INVALID_STRING")
        try:
            exchange = HttpExchangeReader.from_json(json_string)
            raise AssertionError("No exception raised from invalid timestamp")
        except ValueError as e:
            assert str(e).startswith("Invalid isoformat string")


def test_from_jsonl():
    with open(SAMPLE_JSONL, "r", encoding="utf-8") as f:
        exchanges = list(HttpExchangeReader.from_jsonl(f))
        validate_sample_exchanges(exchanges)


def validate_sample_exchanges(exchanges):
    assert len(exchanges) == 3
    assert exchanges[0]['request']['protocol'] == "http"
    assert exchanges[1]['request']['protocol'] == "https"

    for exchange in exchanges[0:2]:
        assert exchange['request']['path'] == '/user/repos?q=v'
        assert exchange['request']['pathname'] == '/user/repos'
        assert exchange['request']['query'] == {'q': "v"}

    assert exchanges[2]['request']['path'] == '/user/repos'
    assert exchanges[2]['request']['pathname'] == '/user/repos'
    assert exchanges[2]['request']['query'] == {}


def test_writing_json():
    buffer = StringIO()
    writer = HttpExchangeWriter(buffer)

    original_exchanges = []
    with open(SAMPLE_JSONL, "r", encoding="utf-8") as f:
        for exchange in HttpExchangeReader.from_jsonl(f):
            original_exchanges.append(exchange)
            writer.write(exchange)

    buffer.seek(0)
    exchanges = list(HttpExchangeReader.from_jsonl(buffer))
    validate_sample_exchanges(exchanges)
    assert original_exchanges == exchanges
