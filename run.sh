#!/usr/bin/env bash

VENV_ROOT=~/.venvs
SCRIPT_VENV_PATH=$VENV_ROOT/dynamic-ip-cloudflare

if [ ! -d $SCRIPT_VENV_PATH ]; then
    if [ ! -d $VENV_ROOT ]; then
        mkdir -p $VENV_ROOT
    fi
    python3 -m venv $SCRIPT_VENV_PATH
fi

source $SCRIPT_VENV_PATH/bin/activate

python3 -m pip install -r requirements.txt

python3 main.py