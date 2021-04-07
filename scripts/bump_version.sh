#!/bin/sh -e

current_version=$(python -c "import astrobase_cli; print(astrobase_cli.__version__)")
echo "current version: $current_version"
read -p "new version: " new_version

sed -i '' -e "s/$current_version/$new_version/g" astrobase_cli/__init__.py
