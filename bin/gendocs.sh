#!/bin/bash
if test -f bin/sphinx-build; then
    SPHINXBUILD=bin/sphinx-build
else
    SPHINXBUILD=../bin/sphinx-build
fi

$SPHINXBUILD -b  html docs/source docs/help
