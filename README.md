# HTTP types in Python

[![CircleCI](https://circleci.com/gh/Meeshkan/py-http-types.svg?style=shield)](https://circleci.com/gh/Meeshkan/py-http-types)
[![PyPi](https://img.shields.io/pypi/pyversions/http-types)](https://pypi.org/project/http-types/)
[![License](https://img.shields.io/pypi/l/http-types)](LICENSE)

Types for HTTP request and response.

Requires **Python >= 3.6**.

## Installation

```bash
pip install http-types
```

## Usage

### Creating objects by hand

You can create typed `Request` and `Response` objects directly by listing arguments:

```py
from http_types import Request, Response, RequestBuilder

req = Request(method="get",
              host="api.github.com",
              path="/user/repos?id=1",
              pathname="/user/repos",
              protocol="https",
              query={"id": ["1"]},
              body="",
              bodyAsJson="",
              headers={})  # Valid `Request` object, passes type-checking

res = Response(statusCode=200, body="OK", headers={})  # Valid `Response` object, passes type-checking

invalid_req = Request(method="get")  # Fails type-checking, missing arguments
invalid_res = Response(body=1, ...)  # Fails type-checking, wrong type for `body`
```

### Creating objects via helper methods

```py
from http_types import RequestBuilder, ResponseBuilder, HttpExchangeBuilder

# Create Request object from URL
url = "https://api.github.com/v1/repos?id=1"
req = RequestBuilder.from_url(url)  # Validated Request object

# Create request object from dictionary
req_obj = {
    'host': 'api.github.com',
    'protocol': 'https',
    'method': 'get',
    'path': '/v1/users',  # pathname inferred automatically
    'query': {}
}
req = RequestBuilder.from_dict(req_obj)  # `body`, `pathname`, and `headers` are optional
```

### Validating objects

```py
from http_types import RequestBuilder, ResponseBuilder

req = Request(...)
RequestBuilder.validate(req)  # Validate `Request` object

res = Response(...)
ResponseBuilder.validate(res)  # Validate `Response` object
```

## Development

### Local development

1. Create a new virtual environment.
1. Install dependencies: `pip install --upgrade -e '.[dev]'`
1. Install [pyright](https://github.com/microsoft/pyright).

### Running tests

Run `python setup.py test`, which will:

- Enforce code formatting using [black](https://black.readthedocs.io/en/stable/).
- Test with `pytest`, configured in [pytest.ini](./pytest.ini).
- Type check with `pyright`, configured in [pyrightconfig.json](./pyrightconfig.json).
- Enforce style guide with [flake8](https://flake8.pycqa.org/en/latest/), configured in [.flake8](./.flake8).

### Publishing package

1. Bump the version in [setup.py](./setup.py) if the version is the same as in the published [package](https://pypi.org/project/http-types/). Commit and push.
1. Run `python setup.py test`, `python setup.py typecheck` and `python setup.py dist` to check everything works
1. To build and upload the package, run `python setup.py upload`. Insert PyPI credentials to upload the pacakge to `PyPI`. The command will also run `git tag` to tag the commit as a release and push the tags to remote.

To see what the different commands do, see `Command` classes in [setup.py](./setup.py).
