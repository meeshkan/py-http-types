from http_types import Request, Response
from typeguard import check_type  # type:ignore

req = Request(method="get",
              host="api.github.com",
              path="/user/repos?id=1",
              pathname="/user/repos",
              protocol="https",
              query={"id": ["1"]},
              body="",
              body_as_json="",
              headers={})

res = Response(status_code=200, body="OK", body_as_json="OK", headers={})


def test_request_typechecks():
    check_type("req", req, Request)


def test_response_typechecks():
    check_type("res", res, Response)
