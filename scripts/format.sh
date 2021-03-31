#!/bin/sh -ex

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place cli tests --exclude=__init__.py
black cli tests
isort cli tests
