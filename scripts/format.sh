#!/bin/sh -ex

# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports cli tests

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place cli tests --exclude=__init__.py
black cli tests
isort cli tests
