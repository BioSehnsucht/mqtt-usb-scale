#!/usr/bin/python
import os, time
import usb.core
import usb.util
import sys
import configparser
import paho.mqtt.client as paho
import json
from enum import Enum
from struct import unpack

class Report(Enum):
    Unknown = 0
    Attr = 1
    Control = 2
    Data = 3
    Status = 4
    Limit = 5
    Stats = 6

    def __str__(self):
        if self.value == self.Attr.value: return 'Attribute'
        if self.value == self.Control.value: return 'Control'
        if self.value == self.Data.value: return 'Data'
        if self.value == self.Status.value: return 'Status'
        if self.value == self.Limit.value: return 'Limit'
        if self.value == self.Stats.value: return 'Stats'
        return 'Unknown'

class Status(Enum):
    Unknown = 0
    Fault = 1
    Zeroed = 2
    Retry = 3
    Positive = 4
    Negative = 5
    Overload = 6
    Calibrate = 7
    Rezero = 8

    def __str__(self):
        if self.value == self.Fault.value: return 'Fault'
        if self.value == self.Zeroed.value: return 'Zeroed'
        if self.value == self.Retry.value: return 'Retry'
        if self.value == self.Positive.value: return 'Positive'
        if self.value == self.Negative.value: return 'Negative'
        if self.value == self.Overload.value: return 'Overload'
        if self.value == self.Calibrate.value: return 'Calibrate'
        if self.value == self.Rezero.value: return 'Rezero'
        return 'Unknown'

class Unit(Enum):
    Unknown = 0
    Milligram = 1
    Gram = 2
    Kilogram = 3
    Carat = 4
    Taels = 5
    Grain = 6
    Pennyweight = 7
    MetricTon = 8
    AvoirTon = 9
    TroyOunce = 10
    Ounce = 11
    Pound = 12

    def __str__(self):
        if self.value == self.Milligram.value: return 'mg'
        if self.value == self.Gram.value: return 'g'
        if self.value == self.Kilogram.value: return 'kg'
        if self.value == self.Carat.value: return 'cd'
        if self.value == self.Taels.value: return 'taels'
        if self.value == self.Grain.value: return 'gr'
        if self.value == self.Pennyweight.value: return 'dwt'
        if self.value == self.MetricTon.value: return 't'
        if self.value == self.AvoirTon.value: return 'avoir t'
        if self.value == self.TroyOunce.value: return 'oz t'
        if self.value == self.Ounce.value: return 'oz'
        if self.value == self.Pound.value: return 'lb'
        return 'Unknown'

class Scale:
    def __init__(self, vendorId = None, productId = None):
        self._report = None
        self._status = None
        self._unit = None
        self._exponent = None
        self._rawWeight = None
        self._weight = None
        self._vendorId = None
        self._productId = None
        self._dev = None
        self._interface = None
        self._endpoint = None
        self._failures = 0

        if ((vendorId is not None) and (productId is not None)):
            self._vendorId = vendorId
            self._productId = productId
        #else
        #   Detect it somehow    

        self.attach()

    def parse(self, data):
        if data is None:
            self._failures = self._failures + 1
            return False
        self._report = Report(data[0])
        self._status = Status(data[1])
        self._unit = Unit(data[2])
        self._exponent = unpack('b', bytes([data[3]]))[0]
        self._rawWeight = data[4] + (data[5] << 8)

        if ((self._report == Report.Data) and (self._status == Status.Positive)):
            self._failures = 0
            self._weight = self._rawWeight * pow(10, self._exponent)
            # TODO : Unit scaling
            return self._weight
        
        return False

    @property
    def unit(self):
        return str(self._unit)
       
    @property
    def failures(self):
        return self._failures
 
    def dump(self):
        print(str(self._report))
        print(str(self._status))
        print(str(self._unit))
        print(str(self._exponent))
        print(str(self._rawWeight))
        print(str(self._weight))

    def attach(self):
        try:
            self._dev = usb.core.find(idVendor=self._vendorId, idProduct=self._productId)
            self._interface = 0

            if self._dev is None:
                print ("device not found")
                return False
            else:
                if self._dev.is_kernel_driver_active(self._interface) is True:
                    #print ("but we need to detach kernel driver")
                    self._dev.detach_kernel_driver(self._interface)

                    # use the first/default configuration
                    self._dev.set_configuration()
                    #print ("claiming device")
                    usb.util.claim_interface(self._dev, self._interface)
        except Exception as e:
            print (e)
            return False

    def release(self):
        try:
            #print ("release claimed interface")
            usb.util.release_interface(self._dev, self._interface)
            #print ("now attaching the kernel driver again")
            self._dev.attach_kernel_driver(self._interface)
            #print ("all done")
        except Exception as e:
            print (e)


    def grab(self):
        try:
            self._endpoint = self._dev[0][(0,0)][0]
            # read a data packet
            attempts = 10
            data = None
            while data is None and attempts > 0:
                time.sleep(0.1)
                attempts -= 1
                try:
                    data = self._dev.read(self._endpoint.bEndpointAddress, self._endpoint.wMaxPacketSize)
                except usb.core.USBError as e:
                    data = None
                    if 'Operation timed out' in e.args:
                        print ("timed out... trying again")
                        continue
            if data is not None:
                weight = self.parse(data)
                return weight
            else:
                self._failures = self._failures + 1
                print("error reading")
                return False
        except usb.core.USBError as e:
            print ("USBError: " + str(e.args))
        except IndexError as e:
            print ("IndexError: " + str(e.args))

def main():
    if len(sys.argv) < 2:
        print("Usage: mqtt-usb-scale <config file>")
        sys.exit()
    configfile = sys.argv[1]
    
    config = configparser.ConfigParser()
    config.read(configfile)

    broker = paho.Client('test')
    broker_address = config.get('broker','address').encode('utf-8')
    broker_port = config.getint('broker','port')
    broker_username = config.get('broker','username')
    broker_password = config.get('broker','password')
    broker.username_pw_set(broker_username, broker_password)
    broker.connect(broker_address,broker_port)

    topic_root = config.get('sensor','topic')
    topic_config = topic_root + '/config'
    topic_state = topic_root + '/state'
    loop_interval = config.getint('sensor','interval')
    scale_name = config.get('sensor','name')
    scale_vendor = int(config.get('sensor','vendor_id'),16)
    scale_product = int(config.get('sensor','product_id'),16)

    try:
        scale = Scale(vendorId=scale_vendor, productId=scale_product)
        if scale.attach() is False:
            sys.exit()                    
        else:
            print ("listening for weight...")

            unique_id = 'pyscale ' + scale_name
            unique_id = unique_id.replace(' ','_')
            payload_config = {
                'name' : scale_name,
                'state_topic' : topic_state,
                'unique_id' : unique_id
            }

            max_failures = 3

            while (scale.failures < max_failures):
                weight = 0

                weight = scale.grab()
                if weight:
                    print("publishing weight")
                    payload_config['unit_of_measurement'] = scale.unit
                    payload_state = int(round(float(weight)))
                    broker.publish(topic_config,json.dumps(payload_config))
                    broker.publish(topic_state,json.dumps(payload_state))
                time.sleep(loop_interval)
            if (scale.failures >= max_failures):
                print ("Too many failures reading device, device unplugged? Exiting.")

    except KeyboardInterrupt as e:
        scale.release()
        print ("\nCtrl-C pressed, exiting.")
        sys.exit();

main()
