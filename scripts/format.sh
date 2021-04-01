#!/bin/sh -ex

# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports main.py cli tests

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place main.py cli tests --exclude=__init__.py
black main.py cli tests
isort main.py cli tests
