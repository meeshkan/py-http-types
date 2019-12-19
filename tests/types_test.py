from http_types import Request, Response
from typeguard import check_type  # type:ignore

req = Request(method="get",
              host="api.github.com",
              path="/user/repos?id=1",
              pathname="/user/repos",
              protocol="https",
              query={"id": ["1"]},
              body="",
              bodyAsJson="",
              headers={})

res = Response(statusCode=200, body="OK", bodyAsJson="OK", headers={})


def test_request_typechecks():
    check_type("req", req, Request)


def test_response_typechecks():
    check_type("res", res, Response)
