#!/bin/bash

pyenv virtualenv agora-api
pyenv local agora-api
pip install --upgrade pip
flask run