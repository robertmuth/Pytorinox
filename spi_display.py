#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple SPI display helper supports updates from a PIL.Image
for the following drivers:

SSD1306
SSD1327
SH1106
IL3820

A lot of the code was inspired by Richard Hull's excellent luma.oled library.

Optional Dependencies:
spidev
RPi.GPIO

Demo/Test (you will likely need to configure it):
./spi_display.py
"""

import time

# spidev and RPi.GPIO are necessary to instantiate a SpiDevice
# But it is possible to provide your own object that behaves
# like an SpiDevice.
try:
    import spidev
except:
    print("spidev lib not available")

try:
    import RPi.GPIO as GPIO
except:
    print("GPIO lib not available")

from PIL import Image, ImageDraw, ImageFont

# common
SETREMAP = 0xA0
DISPLAYALLON_RESUME = 0xA4
DISPLAYALLON = 0xA5
NORMALDISPLAY = 0xA6
INVERTDISPLAY = 0xA7
SETMULTIPLEX = 0xA8
DISPLAYOFF = 0xAE
DISPLAYON = 0xAF

SETCONTRAST = 0x81

# 1306 + SH1106
CHARGEPUMP = 0x8D
COLUMNADDR = 0x21
COMSCANDEC = 0xC8
COMSCANINC = 0xC0
EXTERNALVCC = 0x1
MEMORYMODE = 0x20
PAGEADDR = 0x22
SETCOMPINS = 0xDA
SETDISPLAYCLOCKDIV = 0xD5
SETDISPLAYOFFSET = 0xD3
SETHIGHCOLUMN = 0x10
SETLOWCOLUMN = 0x00
SETPRECHARGE = 0xD9
SETSEGMENTREMAP = 0xA1
SETSTARTLINE = 0x40
SETVCOMDETECT = 0xDB
SWITCHCAPVCC = 0x2

SSD1322_SETCONTRAST = 0xC1

_SPEEDS = [mhz * 1000000 for mhz in [0.5, 1, 2, 4, 8, 16, 32]]


class SpiDevice(object):
    """SpiDevice enacapsulates the communiacation with an SPI device.
    """

    def __init__(self, device, port, dc_pin=24, reset_pin=25, busy_pin=None, max_speed_hz=1000 * 1000,
                 transfer_size=4096):
        assert max_speed_hz in _SPEEDS
        self._transfer_size = transfer_size
        self._dc = dc_pin
        self._rst = reset_pin
        self._busy = busy_pin
        if self._dc is not None:
            GPIO.setup(self._dc, GPIO.OUT)
        if self._rst is not None:
            GPIO.setup(self._rst, GPIO.OUT)
        if self._busy is not None:
            GPIO.setup(self._busy, GPIO.IN)
        self.reset()
        self._spi = spidev.SpiDev()
        self._spi.open(device, port)
        self._spi.cshigh = False
        self._spi.max_speed_hz = max_speed_hz = 1000000

    def reset(self):
        if self._rst is not None:
            GPIO.output(self._rst, GPIO.LOW)  # Reset device
            time.sleep(0.2)
            GPIO.output(self._rst, GPIO.HIGH)  # Keep RESET pulled high
            time.sleep(0.2)

    def write_data(self, data: bytes):
        if self._dc is not None:
            GPIO.output(self._dc, GPIO.HIGH)
        # print ("CMD", len(data), list(data))
        i = 0
        n = len(data)
        tx_sz = self._transfer_size
        while i < n:
            # This should accept bytes
            self._spi.writebytes(list(data[i:i + tx_sz]))
            i += tx_sz

    def write_cmd(self, data: bytes):
        if self._dc is not None:
            GPIO.output(self._dc, GPIO.LOW)
        # print ("DATA", len(data), list(data))
        # This should accept bytes
        self._spi.writebytes(list(data))

    def wait_until_idle(self, delay_sec=0.1):
        while GPIO.input(self._busy):
            time.sleep(delay_sec)


def _SSD1306_FramebufferUpdateData(w, h, image: Image):
    assert image.mode == "1"
    pages = h // 8
    out = bytearray(w * pages)
    for i, pix in enumerate(image.getdata()):
        if pix > 0:
            off = (w * (i // (w * 8))) + (i % w)
            mask = 1 << (i // w) % 8
            out[off] |= mask
    return out


def _SSD1306_FramebufferUpdateDataXXX(w, h, image: Image):
    pages = h // 8
    out = bytearray(w * pages)
    val = 0
    for i, pix in enumerate(image.getdata()):
        val <<= 1
        if pix > 0:
            val |= 1
        if i % 8 == 7:
            out[i // 8] = val
            val = 0
    return out


_SSD1306_SETTINGS = {
    (128, 64): dict(multiplex=0x3F, displayclockdiv=0x80, compins=0x12),
    (128, 32): dict(multiplex=0x1F, displayclockdiv=0x80, compins=0x02),
    (96, 16): dict(multiplex=0x0F, displayclockdiv=0x60, compins=0x02),
    (64, 48): dict(multiplex=0x2F, displayclockdiv=0x80, compins=0x12),
    (64, 32): dict(multiplex=0x1F, displayclockdiv=0x80, compins=0x12),
}


# https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf
class SSD1306(object):

    def __init__(self, dev, w=128, h=64):
        self._dev = dev
        self._w = w
        self._h = h
        self.size = (w, h)
        settings = _SSD1306_SETTINGS.get((w, h))
        colstart = (0x80 - w) // 2
        pages = h // 8
        self._update_cmd = bytes([
            COLUMNADDR, colstart, colstart + w - 1,
            PAGEADDR, 0, pages - 1,
        ])
        init_cmd = bytes([
            DISPLAYOFF,
            SETDISPLAYCLOCKDIV, settings['displayclockdiv'],
            SETMULTIPLEX, settings['multiplex'],
            SETDISPLAYOFFSET, 0x00,
            SETSTARTLINE,
            CHARGEPUMP, 0x14,
            MEMORYMODE, 0x00,
            SETSEGMENTREMAP,
            COMSCANDEC,
            SETCOMPINS, settings['compins'],
            SETPRECHARGE, 0xF1,
            SETVCOMDETECT, 0x40,
            DISPLAYALLON_RESUME,
            NORMALDISPLAY,
            SETCONTRAST, 207,
        ])
        self._dev.write_cmd(init_cmd)

    def show(self, image: Image):
        data = _SSD1306_FramebufferUpdateData(self._w, self._h, image)
        self._dev.write_cmd(self._update_cmd)
        self._dev.write_data(data)

    def on(self):
        self._dev.write_cmd(bytes([DISPLAYON]))

    def off(self):
        self._dev.write_cmd(bytes([DISPLAYOFF]))


def _SSD1327_FramebufferUpdateData(image):
    assert image.mode == "1"
    assert image.size == (128, 128)
    w, h = image.size
    out = bytearray(w * h // 2)
    nibble = 0
    for i, pix in enumerate(image.getdata()):
        if i & 1 == 0:
            nibble = (pix >> 4)
        else:
            out[i // 2] = nibble | pix & 0xf0
    return out


class SSD1327(object):
    def __init__(self, dev):
        self._dev = dev
        self._w = 128
        self._h = 128
        self.size = (self._w, self._h)
        self._update_cmd = bytes([
            0x15, 0, self._w - 1,
            0x75, 0, self._h - 1,
        ])
        init_cmd = bytes([
            DISPLAYOFF,  # Display off (all pixels off)
            # gment remap (com split, com remap, nibble remap, column remap)
            SETREMAP, 0x53,
            0xA1, 0x00,  # Display start line
            0xA2, 0x00,  # Display offset
            DISPLAYALLON_RESUME,  # regular display
            SETMULTIPLEX, 0x7F,  # set multiplex ratio: 127
            0xB8, 0x01, 0x11, 0x22, 0x32, 0x43, 0x54, 0x65, 0x76,  # Set greyscale table
            0xB3, 0x00,  # Front clock divider: 0, Fosc: 0
            0xAB, 0x01,  # Enable Internal Vdd
            0xB1, 0xF1,  # Set phase periods - 1: 1 clk, 2: 15 clks
            0xBC, 0x08,  # Pre-charge voltage: Vcomh
            0xBE, 0x07,  # COM deselect voltage level: 0.86 x Vcc
            0xD5, 0x62,  # Enable 2nd pre-charge
            0xB6, 0x0F,  # 2nd Pre-charge period: 15 clks
            SETCONTRAST, 127,
        ])
        self._dev.write_cmd(init_cmd)

    def show(self, image: Image):
        data = _SSD1327_FramebufferUpdateData(image)
        self._dev.write_cmd(self._update_cmd)
        self._dev.write_data(data)

    def on(self):
        self._dev.write_cmd(bytes([DISPLAYON]))

    def off(self):
        self._dev.write_cmd(bytes([DISPLAYOFF]))


_SH1106_SETTINGS = {
    (128, 128): dict(multiplex=0xFF, displayoffset=0x02),
    (128, 64): dict(multiplex=0x3F, displayoffset=0x00),
    (128, 32): dict(multiplex=0x20, displayoffset=0x0F)
}


def _SH1106_FramebufferUpdateData(image):
    assert image.mode == "1"
    w, h = image.size
    data = image.getdata()
    buf = bytearray(w * h // 8)
    # A page consists of 8 pixel rows
    page_size_pixels = 8 * w
    for i in range(0, w * h, page_size_pixels):
        o = i // 8
        for j in range(w):
            d = 0
            for k in range(8):
                if data[i + j + k * w] > 0:
                    d |= 1 << k
            buf[o + j] = d
    return buf


class SH1106(object):
    def __init__(self, dev, w, h):
        self._dev = dev
        self._w = w
        self._h = h
        self.size = (w, h)
        settings = _SH1106_SETTINGS.get((w, h))
        init_cmd = bytes([
            DISPLAYOFF,
            MEMORYMODE,
            SETHIGHCOLUMN, 0xB0, 0xC8,
            SETLOWCOLUMN, 0x10, 0x40,
            SETSEGMENTREMAP,
            NORMALDISPLAY,
            SETMULTIPLEX, settings['multiplex'],
            DISPLAYALLON_RESUME,
            SETDISPLAYOFFSET, settings['displayoffset'],
            SETDISPLAYCLOCKDIV, 0xF0,
            SETPRECHARGE, 0x22,
            SETCOMPINS, 0x12,
            SETVCOMDETECT, 0x20,
            SETCONTRAST, 127,
        ])
        self._dev.write_cmd(init_cmd)

    def show(self, image: Image):
        data = _SH1106_FramebufferUpdateData(image)
        page_size_bytes = image.size[0]
        update_cmd = bytearray([0xB0, 0x02, 0x10])
        for i in range(0, len(data), page_size_bytes):
            self._dev.write_cmd(bytes(update_cmd))
            update_cmd[0] += 1
            self._dev.write_data(data[i:i + page_size_bytes])

    def on(self):
        self._dev.write_cmd(bytes([DISPLAYON]))

    def off(self):
        self._dev.write_cmd(bytes([DISPLAYOFF]))


# EPD2IN9 commands
DRIVER_OUTPUT_CONTROL = 0x01
BOOSTER_SOFT_START_CONTROL = 0x0C
GATE_SCAN_START_POSITION = 0x0F
DEEP_SLEEP_MODE = 0x10
DATA_ENTRY_MODE_SETTING = 0x11
SW_RESET = 0x12
TEMPERATURE_SENSOR_CONTROL = 0x1A
MASTER_ACTIVATION = 0x20
DISPLAY_UPDATE_CONTROL_1 = 0x21
DISPLAY_UPDATE_CONTROL_2 = 0x22
WRITE_RAM = 0x24
WRITE_VCOM_REGISTER = 0x2C
WRITE_LUT_REGISTER = 0x32
SET_DUMMY_LINE_PERIOD = 0x3A
SET_GATE_TIME = 0x3B
BORDER_WAVEFORM_CONTROL = 0x3C
SET_RAM_X_ADDRESS_START_END_POSITION = 0x44
SET_RAM_Y_ADDRESS_START_END_POSITION = 0x45
SET_RAM_X_ADDRESS_COUNTER = 0x4E
SET_RAM_Y_ADDRESS_COUNTER = 0x4F
TERMINATE_FRAME_READ_WRITE = 0xFF

_lut_partial_update = [
    0x10, 0x18, 0x18, 0x08, 0x18, 0x18, 0x08, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x13, 0x14, 0x44, 0x12,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]


def _IL3820_FramebufferUpdateData(image: Image):
    buf = bytearray(len(image.getdata()) // 8)
    pix8 = 0
    for n, x in enumerate(image.getdata()):
        pix8 <<= 1
        if x:
            pix8 |= 1
        if n & 0x7 == 7:
            buf[n >> 3] = pix8
            pix8 = 0
    return buf


# https://www.waveshare.com/wiki/2.9inch_e-Paper_Module
# https://www.smart-prototyping.com/image/data/9_Modules/EinkDisplay/GDE029A1/IL3820.pdf
class IL3820:

    def __init__(self, dev: SpiDevice, w=128, h=296):
        self._dev = dev
        self._w = w
        self._h = h
        self.size = (w, h)
        self._dev.reset()
        h = self._h - 1
        self._send_command(DRIVER_OUTPUT_CONTROL, [h & 0xff, h >> 8, 0])
        self._send_command(BOOSTER_SOFT_START_CONTROL, [0xD7, 0xD6, 0x9D])
        self._send_command(WRITE_VCOM_REGISTER, [0xa8])  # VCOM 7C
        # 4 dummy lines per gate
        self._send_command(SET_DUMMY_LINE_PERIOD, [0x1A])
        self._send_command(SET_GATE_TIME, [0x08])  # 2us per line
        # X increment Y increment
        self._send_command(DATA_ENTRY_MODE_SETTING, [0x03])
        self._send_command(WRITE_LUT_REGISTER, _lut_partial_update)
        self._set_memory_area(0, 0, self._w - 1, self._h - 1)
        self._set_memory_pointer(0, 0)

    def _send_command(self, command, data=None):
        self._dev.write_cmd(bytes([command]))
        if data:
            self._dev.write_data(bytes(data))

    def show(self, image):
        # TODO: implement partial updates
        assert image.mode == "1"
        assert image.size == (self._w, self._h)

        self._dev.wait_until_idle()
        self._send_command(WRITE_RAM)
        self._dev.write_data(_IL3820_FramebufferUpdateData(image))
        self._display_frame()

    def _display_frame(self):
        self._send_command(DISPLAY_UPDATE_CONTROL_2, [0xC4])
        self._send_command(MASTER_ACTIVATION)
        self._send_command(TERMINATE_FRAME_READ_WRITE)

    def _set_memory_area(self, x_start, y_start, x_end, y_end):
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self._send_command(SET_RAM_X_ADDRESS_START_END_POSITION, [
                           x_start >> 3, x_end >> 3])
        self._send_command(SET_RAM_Y_ADDRESS_START_END_POSITION,
                           [y_start & 0xFF, y_start >> 8, y_end & 0xFF, y_end >> 8])

    def _set_memory_pointer(self, x, y):
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self._send_command(SET_RAM_X_ADDRESS_COUNTER, [x >> 3])
        self._send_command(SET_RAM_Y_ADDRESS_COUNTER, [y & 0xff, y >> 8])

    def sleep(self):
        self._send_command(DEEP_SLEEP_MODE)

    def on(self):
        pass

    def off(self):
        pass


_MAX7219_NOOP = 0x00
_MAX7219_DIGIT_0 = 0x01
_MAX7219_DECODEMODE = 0x09
_MAX7219_INTENSITY = 0x0A
_MAX7219_SCANLIMIT = 0x0B
_MAX7219_SHUTDOWN = 0x0C
_MAX7219_DISPLAYTEST = 0x0F


class MAX7219:

    def __init__(self, dev: SpiDevice, w=8, h=8):
        self._dev = dev
        self._w = w
        self._h = h
        assert w % 8 == 0
        assert h % 8 == 0
        self.size = (w, h)
        self._num_cascaded = w // 8
        self._init()

    def _init(self):
        self._dev.write_data([_MAX7219_SCANLIMIT, 7] * self._num_cascaded)
        self._dev.write_data([_MAX7219_DECODEMODE, 0] * self._num_cascaded)
        self._dev.write_data([_MAX7219_DISPLAYTEST, 0] * self._num_cascaded)

    def show(self, image: Image):
        """image upper left will be shown on the end unit in 
        cascasding set of units
        """

        assert image.mode == "1"
        assert image.size == self.size
        b = 0
        # we go one row at a time: pixels across _num_cascaded devices
        out = bytearray(self._num_cascaded * 2)
        for n, x in enumerate(image.getdata()):
            bit = n & 0x7
            b <<= 1
            if x > 0:
                b |= 1
            if bit == 7:
                row = n // self._w  # [0:7]
                col = (n // 8) % 4  # [0:3]
                out[col * 2] = _MAX7219_DIGIT_0 + row
                out[col * 2 + 1] = b
                if col == 3:
                    self._dev.write_data(out)
                b = 0

    def on(self):
        self._dev.write_data([_MAX7219_SHUTDOWN, 1] * self._num_cascaded)

    def off(self):
        self._dev.write_data([_MAX7219_SHUTDOWN, 0] * self._num_cascaded)

    def brightness(self, level):
        self._dev.write_data(
            [_MAX7219_INTENSITY, level >> 4] * self._num_cascaded)


if __name__ == "__main__":
    import os
    import datetime

    GPIO.setmode(GPIO.BOARD)
    FRAMES = 50

    cwd = os.path.dirname(__file__)
    FONT = ImageFont.truetype(cwd + "/Fonts/code2000.ttf", 25)
    # display = SH1106(SpiDevice(device=0, port=0, dc_pin=18, reset_pin=22), 128, 64)
    # display = SSD1306(SpiDevice(device=0, port=0, dc_pin=18, reset_pin=22), 128, 64)
    # display = IL3820(SpiDevice(device=0, port=0, dc_pin=22, reset_pin=11, busy_pin=18,
    #                           max_speed_hz=2000 * 1000), 128, 296)
    display = MAX7219(SpiDevice(device=0, port=0,
                                dc_pin=None, reset_pin=None, max_speed_hz=500 * 1000), 32, 8)
    print ("dislay size ", display.size)
    fontsize = display.size[1]
    if fontsize > 24:
        fontsize = 24
    print ("font size ", fontsize)
    FONT = ImageFont.truetype(cwd + "/Fonts/code2000.ttf", fontsize)

    display.on()

    def main():
        display.on()
        print("crate and draw into image")
        image = Image.new("1", display.size)
        draw = ImageDraw.Draw(image)
        w, h = image.size

        r = min(*display.size) // 2
        print("radius", r)
        for i in range(r + 1):
            draw.rectangle(((0, 0), image.size), "black")
            draw.rectangle(((i, i), (w - 1 - i, h - 1 - i)), "white")
            display.show(image)
            time.sleep(.5)

        draw.rectangle(((0, 0), image.size), "black")
        now = datetime.datetime.now()
        today_time = now.strftime("%H:%M")
        today_date = now.strftime("%d %b %y")
        draw.text((0, 0), today_time, fill="#fff", font=FONT)
        draw.text((0, 30), today_date, fill="#333", font=FONT)

        print("run simple benchmark: %d times" % FRAMES)
        start = time.time()
        for i in range(FRAMES):
            # copy image into display
            display.show(image)
            time.sleep(0.001)
        stop = time.time()
        print("msec/frame", 1000.0 * (stop - start) / FRAMES)
        time.sleep(2)
        display.off()

    main()
