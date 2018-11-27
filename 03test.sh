#!/bin/sh

coverage run -m unittest discover -s test
coverage report --include="*.py","util/*.py" --omit="test/*.py","venv/*","*/.pyenv/*"
