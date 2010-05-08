#!/bin/bash
if [ $x ]
then
    find . -name '*.py' -type f -exec grep -H "$1" '{}' \; | more
else
    echo "Usage: $0 pattern"
fi
