# HTTP types in Python

[![CircleCI](https://circleci.com/gh/Meeshkan/py-http-types.svg?style=svg)](https://circleci.com/gh/Meeshkan/py-http-types)

Types for HTTP request and response.

Requires **Python >= 3.6**.

## Installation

```bash
pip install http-types
```

## Usage

```bash
from http_types import Request, Response

req = Request(method='get', ...)

# TODO
```

## Development

1. Create a new virtual environment.
1. Install dependencies: `pip install --upgrade -e .[dev]`
1. Run tests: `pytest tests/` or `python setup.py test`
