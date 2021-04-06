#!/bin/sh -ex

# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports astrobase_cli tests

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place astrobase_cli tests --exclude=__init__.py
black astrobase_cli tests
isort astrobase_cli tests
