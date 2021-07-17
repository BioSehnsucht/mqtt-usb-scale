# mqtt-usb-scale
Publish the weight on a USB scale to MQTT for use by Home Assistant or whatever else.

Most regular USB HID Scale class devices should hopefully work - only tested in a Stamps.com 5LB scale however.

Python script should work on any relatively current Linux, though it is only tested on a Pi 3B and Raspbian. Other devices and flavors of linux you may be on your own for installing dependencies or init / systemd setup, etc.

If you want to run more than one scale on a single host device, that should be possible, as long as they have different Vendor / Product IDs - just add another config file, copy the systemd unit file to a new one, modify accordingly, and configure systemd to run it. If they're the same IDs however then the behavior is likely going to be undefined (they may fight over the first device detected, or pick devices at random) - I haven't tested either scenario.

## Known issues
* Some scales zero on startup, so if you have something sitting on it and the Pi reboots, now you're getting a reading of zero. If you have an alert for that, you can know to go remove whatever is sitting on the scale, power cycle the scale, and put it back. It will take a few minutes but between mqtt-usb-scale eventually crashing due to the device going away and systemd restarting it, it should fix itself afterwards.

## Suggested Pi setup
1) May be redundant with the overlayfs below, but I have (after losing a SD card) set `Storage=volatile` in `/etc/systemd/journald.conf` so it only logs to memory.
2) After installing and ensuring everything works as intended, use `raspi-config` Performance options to configure read-only root using overlayfs. This will help prevent SD card wearout - my first SD card wore out after a few months, probably in part due to journald logging of output from mqtt-usb-scale.
3) Consider also disabling any swap that may be configured to use the SD card (either via file or block device - zram type swaps of course won't impact SD).

## How to use:
1) Clone repo to `/opt/mqtt-usb-scale`
2) Connect a compatible USB Scale to your device
3) Copy `/opt/mqtt-usb-scale/mqtt-usb-scale.conf.template` to `/opt/mqtt-usb-scale/mqtt-usb-scale.conf` and edit the values appropriately
4) Run `/opt/mqtt-usb-scale/install.sh` to install systemd unit file
