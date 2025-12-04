#!/bin/bash
# Docker entrypoint script
# TODO: Update the path if you rename the intg-demo folder

cd /usr/src/app
pip install --no-cache-dir -q -r requirements.txt
python intg-demo/driver.py