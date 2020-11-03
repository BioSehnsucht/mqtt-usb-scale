# mqtt-usb-scale
Publish the weight on a USB scale to MQTT for use by Home Assistant or whatever else.

Most regular USB HID Scale class devices should hopefully work - only tested in a Stamps.com 5LB scale however.

Python script should work on any relatively current Linux, though it is only tested on a Pi 3B and Raspbian. Other devices and flavors of linux you may be on your own for installing dependencies or init / systemd setup, etc.

## How to use:
1) Clone repo to `/opt/mqtt-usb-scale`
2) Connect a compatible USB Scale to your device
3) Copy `/opt/mqtt-usb-scale/scale.conf.template` to `/opt/mqtt-usb-scale/scale.conf` and edit the values appropriately
4) Run `/opt/mqtt-usb-scale/install.sh` to install systemd unit file
