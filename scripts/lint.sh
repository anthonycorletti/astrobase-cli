#!/bin/sh -ex

mypy astrobase_cli
flake8 astrobase_cli tests
black astrobase_cli tests --check
isort astrobase_cli tests --check-only
