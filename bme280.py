#!/usr/bin/python3
# cf.: https://github.com/BoschSensortec/BME280_driver/
#      https://cdn.sparkfun.com/assets/learn_tutorials/4/1/9/BST-BME280_DS001-10.pdf

import smbus
import time
import struct
import threading

# Operating Modes
BME280_OSAMPLE_1 = 1
BME280_OSAMPLE_2 = 2
BME280_OSAMPLE_4 = 3
BME280_OSAMPLE_8 = 4
BME280_OSAMPLE_16 = 5

# Standby Settings
BME280_STANDBY_0p5 = 0
BME280_STANDBY_62p5 = 1
BME280_STANDBY_125 = 2
BME280_STANDBY_250 = 3
BME280_STANDBY_500 = 4
BME280_STANDBY_1000 = 5
BME280_STANDBY_10 = 6
BME280_STANDBY_20 = 7

# Filter Settings
BME280_FILTER_OFF = 0
BME280_FILTER_2 = 1
BME280_FILTER_4 = 2
BME280_FILTER_8 = 3
BME280_FILTER_16 = 4

BME280_REGISTER_DIG_T1 = 0x88
BME280_REGISTER_DIG_P1 = 0x8E
BME280_REGISTER_DIG_H1 = 0xA1
BME280_REGISTER_DIG_H2 = 0xE1

BME280_REGISTER_CHIPID = 0xD0
BME280_REGISTER_VERSION = 0xD1
BME280_REGISTER_SOFTRESET = 0xE0

BME280_REGISTER_STATUS = 0xF3
BME280_REGISTER_CONTROL_HUM = 0xF2
BME280_REGISTER_CONTROL = 0xF4
BME280_REGISTER_CONFIG = 0xF5
BME280_REGISTER_DATA = 0xF7

MAGIC_BMP280 = 0x58
MAGIC_BME280 = 0x60


def SetMode(device, hmode=BME280_OSAMPLE_1, pmode=BME280_OSAMPLE_1, tmode=BME280_OSAMPLE_1,
            standby=BME280_STANDBY_250, filter=BME280_FILTER_OFF):
    device.write(BME280_REGISTER_CONTROL_HUM, [hmode])
    time.sleep(0.002)

    device.write(BME280_REGISTER_CONFIG, [(standby << 5) | (filter << 2)])
    time.sleep(0.002)

    # Select Control measurement register, 0xF4(244)
    device.write(BME280_REGISTER_CONTROL, [(tmode << 5) | (pmode << 2) | 3])
    time.sleep(0.002)


def ReadRawMeasurements(device):
    # wait for data to become available
    while (device.read(BME280_REGISTER_STATUS, 1)[0] & 0x08):
        print("#####")
        time.sleep(0.002)

    # Read data back from 0xF7(247), 8 bytes
    data = device.read(BME280_REGISTER_DATA, 8)

    # Convert pressure and temperature data to 19-bits
    adc_p = (data[0] * 65536 + data[1] * 256 + (data[2] & 0xF0)) / 16
    adc_t = (data[3] * 65536 + data[4] * 256 + (data[5] & 0xF0)) / 16

    # Convert the humidity data
    adc_h = data[6] * 256 + data[7]
    return adc_h, adc_p, adc_t


def ComputeTemp(adc_t, tcal):
    t1, t2, t3 = tcal
    # Temperature offset calculations
    v1 = adc_t / 16384.0 - t1 / 1024.0
    v2 = adc_t / 131072.0 - t1 / 8192.0
    return v1 * t2 + v2 * v2 * t3


def ComputePressure(adc_p, t_fine, pcal):
    p1, p2, p3, p4, p5, p6, p7, p8, p9 = pcal
    # Pressure offset calculations
    var1 = t_fine / 2.0 - 64000.0
    var2 = var1 * var1 * p6 / 32768.0
    var2 = var2 + var1 * p5 * 2.0
    var2 = var2 / 4.0 + p4 * 65536.0
    var3 = p3 * var1 * var1 / 524288.0
    var1 = (var3 + p2 * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * p1
    p = 1048576.0 - adc_p
    p = (p - (var2 / 4096.0)) * 6250.0 / var1
    var1 = p9 * p * p / 2147483648.0
    var2 = p * p8 / 32768.0
    return (p + (var1 + var2 + p7) / 16.0) / 100


def ComputeHumidity(adc_h, t_fine, hcal):
    h1, h2, h3, h4, h5, h6 = hcal
    # Humidity offset calculations
    var_H = (t_fine - 76800.0)
    var_H = (adc_h - (h4 * 64.0 + h5 / 16384.0 * var_H)) * (
        h2 / 65536.0 * (1.0 + h6 / 67108864.0 * var_H * (1.0 + h3 / 67108864.0 * var_H)))
    humidity = var_H * (1.0 - h1 * var_H / 524288.0)
    if humidity > 100.0:
        humidity = 100.0
    elif humidity < 0.0:
        humidity = 0.0
    return humidity


def ReadCalibrationData(device):
    # Read data back from 0x88(136), 24 bytes
    buf = device.read(BME280_REGISTER_DIG_T1, 6)
    tcal = struct.unpack("<Hhh", bytes(buf))

    buf = device.read(BME280_REGISTER_DIG_P1, 18)
    pcal = struct.unpack("<Hhhhhhhhh", bytes(buf))

    # Read data back from 0xA1(161), 1 byte
    h1 = device.read(BME280_REGISTER_DIG_H1, 1)[0]

    # Read data back from 0xE1(225), 7 bytes
    b1 = device.read(BME280_REGISTER_DIG_H2, 7)
    # h2, h3, h4, h5, h6 = struct.unpack("<hBh", bytes(b1))

    # Convert the data
    # Humidity coefficients
    h2 = b1[1] * 256 + b1[0]
    if h2 > 32767:
        h2 -= 65536
    h3 = (b1[2] & 0xFF)
    h4 = (b1[3] * 16) + (b1[4] & 0xF)
    if h4 > 32767:
        h4 -= 65536
    h5 = (b1[4] // 16) + (b1[5] * 16)
    if h5 > 32767:
        h5 -= 65536
    h6 = b1[6]
    if h6 > 127:
        h6 -= 256
    return (h1, h2, h3, h4, h5, h6), pcal, tcal


def ReadCalibrationData680(device):
    buf = device.read(0x89, 2) + device.read(0x89, 4)
    tcal = struct.unpack("<Hhh", bytes(buf))
    print (tcal)


def ReadMeasurements(device, hcal, pcal, tcal):
    adc_h, adc_p, adc_t = ReadRawMeasurements(device)
    t_fine = ComputeTemp(adc_t, tcal)
    temp = t_fine / 5120.0

    pressure = ComputePressure(adc_p, t_fine, pcal)
    humidity = ComputeHumidity(adc_h, t_fine, hcal)

    return temp, pressure, humidity


# This also supports BMP280 (the humidity will read as 0.0)
class SensorBME280:

    def __init__(self, device, addr=0x76, interval=60):
        self._device = device
        self._addr = addr
        assert device.read(BME280_REGISTER_CHIPID, 1)[
            0] in [MAGIC_BME280, MAGIC_BMP280]
        self._interval = interval
        self._hcal, self._pcal, self._tcal = ReadCalibrationData(device)
        SetMode(device)
        self._last = 0
        self._temp = None
        self._pressure = None
        self._humidity = None
        self.Update()

    def Update(self):
        print("update")
        self._last = time.time()
        self._temp, self._pressure, self._humidity = ReadMeasurements(
            self._device, self._hcal, self._pcal, self._tcal)

    def ReadMeasurements(self):
        if self._last + self._interval < time.time():
            threading.Thread(target=self.Update).start()
        return self._temp, self._pressure, self._humidity

    def ReadMeasurementsFresh(self):
        self.Update()
        return self._temp, self._pressure, self._humidity

    def RenderMeasurements(self):
        return "%.1f\u00B0C %.0f hPa %.1f%%" % self.ReadMeasurements()


class I2CDevice:

    def __init__(self, bus_no=1, addr=0x76, debug=False):
        """Initialize the I2C device at the 'address' given"""
        self._bus = smbus.SMBus(bus_no)
        self._addr = addr
        self._debug = debug

    def read(self, register, length):
        """Returns an array of 'length' bytes from the 'register'"""
        result = self._bus.read_i2c_block_data(self._addr, register, length)
        if self._debug:
            print("\t(0x%02x => %s)" % (register, [hex(i) for i in result]))
        return result

    def write(self, register, values):
        """Writes an array of 'length' bytes to the 'register'"""
        for i, value in enumerate(values):
            self._bus.write_byte_data(self._addr, register + i, value)
        if self._debug:
            print("\t(0x%02x <= %s)" %
                  (register, [hex(i) for i in values[0:]]))


if __name__ == "__main__":
    def is_almost_equal(x, y, epsilon=1e-4):
        return abs(x-y) <= epsilon

    class FakeDevice:
        def __init__(self, *pairs):
            r = {}
            self._responses = r
            for a, b in pairs:
                if a not in r:
                    r[a] = []
                r[a].append(b)

        def read(self, register, length):
            #print ("%x %d" % (register, length))
            x = self._responses[register].pop(0)
            assert len(x) == length
            return x

        def write(self, register, values):
            pass

    def test():
        device = FakeDevice(
            (0xd0, [0x60]),
            (0x88, [0xd9, 0x6e, 0x5d, 0x68, 0x32, 0x00]),
            (0x8e, [0xfa, 0x8c, 0xb8, 0xd6, 0xd0, 0xb, 0x4f, 0x17,
                    0xec, 0xff, 0xf9, 0xff, 0x0c, 0x30, 0x20, 0xd1,
                    0x88, 0x13]),
            (0xa1, [0x4b]),
            (0xe1, [0x49, 0x01, 0x00, 0x19, 0x2a, 0x03, 0x1e]),
            (0xf3, [0x0]),
            (0xf7, [0x59, 0x6f, 0x0, 0x80, 0x51, 0x0, 0x7f, 0x4b]))

        sensor = SensorBME280(device)
        temp, pressure, humidity = sensor.ReadMeasurements()
        print("TEST", temp, pressure, humidity)
        assert is_almost_equal(temp, 22.79161)
        assert is_almost_equal(pressure, 1012.05817)
        assert is_almost_equal(humidity, 31.66425)

    def main():
        device = I2CDevice(addr=0x76, debug=True)
        sensor = SensorBME280(device)
        temp, pressure, humidity = sensor.ReadMeasurements()

        print("Temperature in Celsius : %.2f C" % temp)
        print("Pressure : %.2f hPa " % pressure)
        print("Relative Humidity : %.2f %%" % humidity)

    test()
    main()
