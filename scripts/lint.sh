#!/bin/sh -ex

mypy cli
black cli tests --check
isort cli tests --check-only
