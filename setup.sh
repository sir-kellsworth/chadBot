#!/bin/bash

sudo apt install -y $(cat aptRequirements.txt)
pip3 install --user -r python/requirements.txt

wget https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip
unzip chromedriver_linux64.zip

sudo snap install core
sudo snap install runescape
