#!/bin/sh -ex

./scripts/lint.sh

pytest --cov=cli --cov=tests --cov-report=term-missing --cov-report=xml -o console_output_style=progress --numprocesses=auto ${@}
