#!/bin/sh -ex

mypy main.py cli
black main.py cli tests --check
isort main.py cli tests --check-only
