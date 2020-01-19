#!/bin/bash

pyenv virtualenv agora-api
pyenv local agora-api
pip install --upgrade pip
pip install -r requirements.txt

export FLASK_APP=agora-api.py
flask run -p 6006