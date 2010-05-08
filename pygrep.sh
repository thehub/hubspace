#!/bin/bash
if [ $1 ]
then
    find . -name '*.py' -type f -exec egrep -H "$1" '{}' \; | more
else
    echo "Usage: $0 pattern"
fi
