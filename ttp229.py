#!/usr/bin/python3
# capacitive touch detector (8 or 16 keys)
# cf.: https://www.elecrow.com/download/TOUCH_IC_TTP229.pdf
#
# TODO: only the 8 key variant seems to work
#       possibly because of a short coming in the smbus2 library

import smbus2

class SensorTTP229:

    def __init__(self, bus=smbus2.SMBus(1), addr=0x57):
        self._bus = bus
        self._addr = addr

    def KeyStatus(self):
        a = self._bus.read_byte(self._addr)
        return a

if __name__ == "__main__":
    import time

    def main():
        sensor = SensorTTP229()
        for i in range(1000):
            print ("%02x" % sensor.KeyStatus())

            time.sleep(0.5)

    main()
