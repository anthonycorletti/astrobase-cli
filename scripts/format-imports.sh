#!/bin/sh -ex

# Sort imports one per line, so autoflake can remove unused imports
isort --force-single-line-imports cli tests
./scripts/format.sh
