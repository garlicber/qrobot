#! /usr/bin/env bash

if [ ! -d ".env" ];then
    virtualenv .env
fi

source .env/bin/activate
pip2 install numpy==1.8.0
pip install --upgrade -r requirements.txt
