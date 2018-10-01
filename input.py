#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Input device helper

Input device helper for  /dev/input/event* devices.
Useful for many USB input devices, including:
keyboards, mice, touchscreen, joysticks

This is in the experimentation stage
"""

import evdev


def _LookupCapability(capabilities, ev_type, ev_code):
    for key, val in capabilities.items():
        print (key, ev_type)
        if key[-1] != ev_type:
            continue
        for v in val:
            if v[-1] != ev_code:
                continue
            return key[0], v[0]
    return "unknown_%s" % ev_type, "unknown_%s" % ev_code,


if __name__ == "__main__":
    import sys


    def DumpEvents(device):
        capabilities = device.capabilities(True)
        print(device.name, device.phys)
        for key, val in capabilities.items():
            print(key)
            for v in val:
                print("   ", v)

        cache = {}
        for event in device.read_loop():
            ev_code = event.code
            ev_type = event.type
            x = cache.get((ev_type, ev_code))
            if not x:
                x = _LookupCapability(capabilities, ev_type, ev_code)
                cache[(ev_type, ev_code)] = x

            print("%5s %10s" % x, event.value)


    if len(sys.argv) == 2:
        print("dumping events for ", sys.argv[1])
        device = evdev.InputDevice(sys.argv[1])
        DumpEvents(device)
    else:
        if len(evdev.list_devices()) == 0:
            print("no devices found - maybe you need to be root")
        else:
            print("Not device path specified. Available devices:")

        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            print(path, device.name, device.phys)
