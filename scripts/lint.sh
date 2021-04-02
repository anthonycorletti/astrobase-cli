#!/usr/bin/env bash -ex

mypy cli
flake8 cli tests
black cli tests --check
isort cli tests --check-only
