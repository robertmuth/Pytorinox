#!/usr/bin/python3
# capacitive touch detector (8 or 16 keys)
# cf.: https://www.elecrow.com/download/TOUCH_IC_TTP229.pdf
# This is a simple i2c device that does not require writing registers

import os
from fcntl import ioctl

# https://elinux.org/Interfacing_with_I2C_Devic
# https://github.com/torvalds/linux/blob/master/include/uapi/linux/i2c-dev.h

# number of times a device address should be polled when not acknowledging
I2C_RETRIES = 0x0701
I2C_TIMEOUT = 0x0702  # set timeout in units of 10 ms
I2C_SLAVE = 0x0703  # Use this slave address
I2C_TENBIT = 0x0704  # 0 for 7 bit addrs, != 0 for 10 bit
I2C_FUNCS = 0x0705  # Get the adapter functionality mask
# Use this slave address, even if it is already in use by a driver!
I2C_SLAVE_FORCE = 0x0706
I2C_RDWR = 0x0707  # Combined R/W transfer (one STOP only)
I2C_PEC = 0x0708  # != 0 to use PEC with SMBus
I2C_SMBUS = 0x0720  # SMBus transfer. Takes pointer to i2c_smbus_ioctl_data


class SensorTTP229:

    def __init__(self, bus_no=1, addr=0x57):
        self._fd = os.open("/dev/i2c-%d" % bus_no, os.O_RDWR)
        self._addr = addr

    def close(self):
        if self._fd:
            os.close(self._fd)
            self._fd = None

    def set_address(self, force=None):
        ioctl(self._fd, I2C_SLAVE, self._addr)

    def KeyStatus(self):
        self.set_address()
        a = os.read(self._fd, 2)
        return a[0] * 256 + a[1]


if __name__ == "__main__":
    import time

    def main():
        sensor = SensorTTP229()
        for i in range(1000):
            print ("%04x" % sensor.KeyStatus())

            time.sleep(0.5)

    main()
