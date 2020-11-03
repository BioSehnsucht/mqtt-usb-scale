#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
set -e
sudo /usr/bin/env pip3 install -r $DIR/requirements.txt
sudo cp $DIR/mqtt-usb-scale.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mqtt-usb-scale.service
sudo systemctl start mqtt-usb-scale.service
