#!/bin/sh -ex

bash ./scripts/lint.sh

pytest --cov=typer --cov=tests --cov-report=term-missing --cov-report=xml -o console_output_style=progress --numprocesses=auto ${@}
