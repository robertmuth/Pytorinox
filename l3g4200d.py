#!/usr/bin/python3
# 3 axis gyroscope
# cf.: https://cdn.sparkfun.com/datasheets/Sensors/Gyros/3-Axis/CD00265057.pdf

import smbus


def _read_s16(bus, addr, reg0, reg1):
    v = bus.read_byte_data(addr, reg0) + 256 * bus.read_byte_data(addr, reg1)
    if v > 32767:
        v -= 65536
    return v


class SensorL3G4200D:

    def __init__(self, bus=smbus.SMBus(1), addr=0x69):
        self._bus = bus
        self._addr = addr
        # setup
        v = self._bus.read_byte_data(self._addr, 0x0f)
        assert v == 0xd3, "wrong device"

        # enable all axes, normal mod
        self._bus.write_byte_data(self._addr, 0x20, 0x0F)
        # Litte Endian, 2000dpsm, no self test, 4 wire
        self._bus.write_byte_data(self._addr, 0x23, 0x30)

    def Rotation(self):
        x = _read_s16(self._bus, self._addr, 0x28, 0x29)
        y = _read_s16(self._bus, self._addr, 0x2a, 0x2b)
        z = _read_s16(self._bus, self._addr, 0x2c, 0x2d)
        return x, y, z

    def Temperature(self):
        return self._bus.read_byte_data(self._addr, 0x26)


if __name__ == "__main__":
    import time

    def main():
        sensor = SensorL3G4200D()
        for i in range(1000):
            x, y, z = sensor.Rotation()
            t = sensor.Temperature()
            print("x %6d  y %6d  z %6d  t %3d" % (x, y, z, t))
            time.sleep(0.5)

    main()
