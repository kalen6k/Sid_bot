#!/bin/bash

pip install "$@"
pip freeze > requirements.txt
