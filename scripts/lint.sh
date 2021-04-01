#!/bin/sh -ex

mypy main.py cli
flake8 main.py cli tests
black main.py cli tests --check
isort main.py cli tests --check-only
