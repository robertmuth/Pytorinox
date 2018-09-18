#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple oled libray - supports display updates from a PIL.Image
for the following drivers:

SSD1306
SSD1327
SH1106

A lot of the code was inspired by Richard Hull's excellent luma.oled library.

Optional Dependencies:
spidev
RPi.GPIO 

Demo/Test (you will likely need to confiure it):
./oled.py
"""

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

    def __init__(self, device, port, dc_pin=24, reset_pin=25, max_speed_hz=1000 * 1000, transfer_size=4096):
        assert max_speed_hz in _SPEEDS
        self._transfer_size = transfer_size
        self._dc = dc_pin
        self._rst = reset_pin
        if self._dc is not None:
            GPIO.setup(self._dc, GPIO.OUT)
        if self._rst is not None:
            GPIO.setup(self._rst, GPIO.OUT)
        self.reset()
        self._spi = spidev.SpiDev()
        self._spi.open(device, port)
        self._spi.cshigh = False
        self._spi.max_speed_hz = max_speed_hz = 1000000

    def reset(self):
        if self._rst is not None:
            GPIO.output(self._rst, GPIO.LOW)  # Reset device
            GPIO.output(self._rst, GPIO.HIGH)  # Keep RESET pulled high

    def write_data(self, data: bytes):
        if self._dc is not None:
            GPIO.output(self._dc, GPIO.HIGH)
        #print ("CMD", len(data), list(data))
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
        settings = _SSD1306_SETTINGS.get((w, h))
        colstart = (0x80 - w) // 2
        pages = h // 8
        self._update_cmd = bytes([
            COLUMNADDR, colstart, colstart + w - 1,
            PAGEADDR, 0,  pages - 1,
        ])
        init_cmd = bytes([
            DISPLAYOFF,
            SETDISPLAYCLOCKDIV, settings['displayclockdiv'],
            SETMULTIPLEX,       settings['multiplex'],
            SETDISPLAYOFFSET,   0x00,
            SETSTARTLINE,
            CHARGEPUMP,         0x14,
            MEMORYMODE,         0x00,
            SETSEGMENTREMAP,
            COMSCANDEC,
            SETCOMPINS,         settings['compins'],
            SETPRECHARGE,       0xF1,
            SETVCOMDETECT,      0x40,
            DISPLAYALLON_RESUME,
            NORMALDISPLAY,
            SETCONTRAST, 207,
        ])
        self._dev.write_cmd(init_cmd)

    def update(self, image: Image):
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
            out[i // 2] = nibble | pix & (0xf0)
    return out


class SSD1327(object):
    def __init__(self, dev):
        self._dev = dev
        self._w = 128
        self._h = 128
        self._update_cmd = bytes([
            0x15, 0, self._w - 1,
            0x75, 0, self._h - 1,
        ])
        init_cmd = bytes([
            DISPLAYOFF,         # Display off (all pixels off)
            # gment remap (com split, com remap, nibble remap, column remap)
            SETREMAP, 0x53,
            0xA1, 0x00,         # Display start line
            0xA2, 0x00,         # Display offset
            DISPLAYALLON_RESUME,        # regular display
            SETMULTIPLEX, 0x7F,         # set multiplex ratio: 127
            0xB8, 0x01, 0x11, 0x22, 0x32, 0x43, 0x54, 0x65, 0x76,   # Set greyscale table
            0xB3, 0x00,         # Front clock divider: 0, Fosc: 0
            0xAB, 0x01,         # Enable Internal Vdd
            0xB1, 0xF1,         # Set phase periods - 1: 1 clk, 2: 15 clks
            0xBC, 0x08,         # Pre-charge voltage: Vcomh
            0xBE, 0x07,         # COM deselect voltage level: 0.86 x Vcc
            0xD5, 0x62,         # Enable 2nd pre-charge
            0xB6, 0x0F,         # 2nd Pre-charge period: 15 clks
            SETCONTRAST, 127,
        ])
        self._dev.write_cmd(init_cmd)

    def update(self, image: Image):
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
    o = 0
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
        settings = _SH1106_SETTINGS.get((w, h))
        init_cmd = bytes([
            DISPLAYOFF,
            MEMORYMODE,
            SETHIGHCOLUMN,      0xB0, 0xC8,
            SETLOWCOLUMN,       0x10, 0x40,
            SETSEGMENTREMAP,
            NORMALDISPLAY,
            SETMULTIPLEX,       settings['multiplex'],
            DISPLAYALLON_RESUME,
            SETDISPLAYOFFSET,   settings['displayoffset'],
            SETDISPLAYCLOCKDIV, 0xF0,
            SETPRECHARGE,       0x22,
            SETCOMPINS,         0x12,
            SETVCOMDETECT,      0x20,
            SETCONTRAST, 127,
        ])
        self._dev.write_cmd(init_cmd)

    def update(self, image: Image):
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


if __name__ == "__main__":
    import os
    import datetime
    import time
    import sys

    GPIO.setmode(GPIO.BOARD)
    FRAMES = 100

    cwd = os.path.dirname(__file__)
    FONT = ImageFont.truetype(cwd + "/Fonts/code2000.ttf", 25)
    # CONFIG = (128, 64, SH1106)
    CONFIG = (128, 64, SSD1306)

    def main():
        w, h, driver_class = CONFIG

        print("crate and draw into image")
        image = Image.new("1", (w, h))
        draw = ImageDraw.Draw(image)
        now = datetime.datetime.now()
        today_time = now.strftime("%H:%M")
        today_date = now.strftime("%d %b %y")
        draw.text((0, 0), today_time, fill="#fff", font=FONT)
        draw.text((0, 30), today_date, fill="#333", font=FONT)

        print("create spi and display devices")
        dev = SpiDevice(device=0, port=0, dc_pin=18, reset_pin=22)
        display = driver_class(dev, w, h)
        display.on()

        # simple benchmark
        start = time.time()
        for i in range(FRAMES):
            # copy image into display
            display.update(image)
            time.sleep(0.001)
            stop = time.time()
        print ("msec/frame", 1000.0 * (stop - start) / FRAMES)
        time.sleep(2)
        display.off()

    main()
