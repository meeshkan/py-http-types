from os import path
import os
import json
from http_types import Request, Response, RequestResponsePair, RequestResponseBuilder
from typeguard import check_type

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
