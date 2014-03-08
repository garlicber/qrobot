#! /usr/bin/env bash

if [ ! -d ".env" ];then
    virtualenv .env
fi

source .env/bin/activate

pip install git+https://github.com/berleon/rgkit.git