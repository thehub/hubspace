#!/bin/bash
if [ $1 ]
echo "Searching for \"$1\""
then
    find . -name '*.py' -type f -exec egrep -i -H "$1" '{}' \; | more
else
    echo "Usage: $0 pattern"
fi
