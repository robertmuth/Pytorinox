#!/usr/bin/python3

"""
Helper for using a rotary switch like this one:
https://www.amazon.com/gp/product/B07DM2YMT4

The rotary encoder has three pins. The middle one
needs to be connected to GND the others to arbitray GPIO pins.
"""

import RPi.GPIO as GPIO


class RotarySwitch(object):
    """ 
    Note, this works better than everything else I tried and does not
    rely on debouncing. It is still not perfect especially when the
    switch is tuned rapidly.

    The callback will be called with True or False depending on the
    direction the switch is turned.

    pina, pinb can be arbitrary GPIO pins
    """

    def __init__(self, pina, pinb, callback):
        self._pina = pina
        self._pinb = pinb
        self._callback = callback
        self._vala = False
        self._valb = False

        GPIO.setup(pina, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(pinb, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pina, GPIO.RISING, callback=self._trigger)
        GPIO.add_event_detect(pinb, GPIO.RISING, callback=self._trigger)

    def _trigger(self, _pin):
        vala = GPIO.input(self._pina)
        valb = GPIO.input(self._pinb)
        if not vala and not valb:
            # time.sleep(0.01)
            return
        if vala == self._vala and valb == self._valb:
            # time.sleep(0.01)
            # print("ignore dups")
            return
        if vala != valb and vala == self._valb and valb == self._vala:
            self._callback(vala)
            vala = True
            valb = True

        self._valb = valb
        self._vala = vala


if __name__ == "__main__":
    import time

    def _example_callback(right):
        print("right" if right else "left")

    GPIO.setmode(GPIO.BOARD)  # Numbers GPIOs by physical location
    rotary = RotarySwitch(10, 8, _example_callback)
    time.sleep(100)
