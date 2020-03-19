# HTTP Types in Python

[![CircleCI](https://circleci.com/gh/meeshkan/py-http-types.svg?style=shield)](https://circleci.com/gh/meeshkan/py-http-types)
[![PyPi](https://img.shields.io/pypi/pyversions/http-types)](https://pypi.org/project/http-types/)
[![License](https://img.shields.io/pypi/l/http-types)](LICENSE)

Python (3.6 or later) library to read and write records of HTTP exchanges in the [HTTP types](https://meeshkan.github.io/http-types/) format.

## Installation

```bash
pip install http-types
```

## Writing HTTP exchanges

Using `HttpExchangeWriter`a recording of HTTP traffic can be serialised for use with any program that can handle the HTTP Types format:

```python
request = RequestBuilder.from_dict({
        "host": "api.github.com",
        "protocol": "https",
        "method": "get",
        "pathname": "/v1/users",
        "query": {"a": "b", "q": ["1", "2"]},
    }
)

response = ResponseBuilder.from_dict({
        "statusCode": 200,
        "headers": {"content-type": "text/plain"},
        "body": "(response body string)",
    }
)

exchange = HttpExchange(request=request, response=response)

with tempfile.TemporaryFile(mode="w") as output:
    writer = HttpExchangeWriter(output)
    writer.write(exchange)

# Serialize to dictionary
as_dict = HttpExchangeWriter.to_dict(exchange)
# Serialize to JSON string
as_str = HttpExchangeWriter.to_json(exchange)
```

## Reading HTTP exchanges

With `HttpExchangeReader` recordings in the HTTP Types format can be read for processing:

```python
for exchange in HttpExchangeReader.from_jsonl(input_file):
    assert exchange.request.method == HttpMethod.GET
    assert exchange.request.protocol == Protocol.HTTPS
    assert exchange.response.statusCode == 200
```

## Development

Initial setup:

1. Create a new virtual environment.
1. Install dependencies: `pip install --upgrade -e '.[dev]'`
1. Install [pyright](https://github.com/microsoft/pyright).

To test, run `python setup.py test`, which will:

- Enforce code formatting using [black](https://black.readthedocs.io/en/stable/).
- Test with `pytest`, configured in [pytest.ini](./pytest.ini).
- Type check with `pyright`, configured in [pyrightconfig.json](./pyrightconfig.json).
- Enforce style guide with [flake8](https://flake8.pycqa.org/en/latest/), configured in [.flake8](./.flake8).

## Publishing

1. Bump the version in [setup.py](./setup.py) if the version is the same as in the published [package](https://pypi.org/project/http-types/). Commit and push.
1. Run `python setup.py test` and `python setup.py dist` to check that everything works.
1. To build and upload the package, run `python setup.py upload`. Insert PyPI credentials to upload the package to `PyPI`. The command will also run `git tag` to tag the commit as a release and push the tags to remote.

To see what the different commands do, see `Command` classes in [setup.py](./setup.py).
