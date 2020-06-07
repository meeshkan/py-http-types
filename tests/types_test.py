from http_types.types import HttpMethod, Protocol
from http_types import Request, Response
from typeguard import check_type  # type:ignore
from datetime import datetime

req = Request(
    method=HttpMethod.GET,
    host="api.github.com",
    path="/user/repos?id=1",
    pathname="/user/repos",
    protocol=Protocol.HTTPS,
    query={"id": ["1"]},
    body="",
    bodyAsJson="",
    headers={},
    timestamp=datetime.now(),
)

res = Response(
    statusCode=200, body="OK", bodyAsJson="OK", headers={}, timestamp=datetime.now()
)


def test_request_typechecks():
    check_type("req", req, Request)


def test_response_typechecks():
    check_type("res", res, Response)


def request_and_response_can_be_instantiated_without_timestamp():
    request = Request(
        method=HttpMethod.GET,
        host="api.github.com",
        path="/user/repos?id=1",
        pathname="/user/repos",
        protocol=Protocol.HTTPS,
        query={"id": ["1"]},
        body="",
        bodyAsJson="",
        headers={},
    )
    assert request.timestamp is None
    response = Response(statusCode=200, body="OK", bodyAsJson="OK", headers={})
    assert response.timestamp is None
