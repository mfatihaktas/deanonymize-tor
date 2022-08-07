#!/bin/bash

isort --skip .direnv/** .
black --exclude=".direnv/*" .
flake8 --exclude=".direnv/*" .
