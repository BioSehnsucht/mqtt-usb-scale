# mqtt-usb-scale
Publish the weight on a USB scale to MQTT for use by Home Assistant or whatever else.

Most regular USB HID Scale class devices should hopefully work - only tested in a Stamps.com 5LB scale however.

Python script should work on any relatively current Linux, though it is only tested on a Pi 3B and Raspbian. Other devices and flavors of linux you may be on your own for installing dependencies or init / systemd setup, etc.

If you want to run more than one scale on a single host device, that should be possible, as long as they have different Vendor / Product IDs - just add another config file, copy the systemd unit file to a new one, modify accordingly, and configure systemd to run it. If they're the same IDs however then the behavior is likely going to be undefined (they may fight over the first device detected, or pick devices at random) - I haven't tested either scenario.

## How to use:
1) Clone repo to `/opt/mqtt-usb-scale`
2) Connect a compatible USB Scale to your device
3) Copy `/opt/mqtt-usb-scale/mqtt-usb-scale.conf.template` to `/opt/mqtt-usb-scale/mqtt-usb-scale.conf` and edit the values appropriately
4) Run `/opt/mqtt-usb-scale/install.sh` to install systemd unit file
