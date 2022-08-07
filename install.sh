#!/bin/bash

direnv allow
pip install --upgrade pip
pip install poetry
poetry install

# pip install -e .
