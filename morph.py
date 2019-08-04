#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Code for morphing text strings
.

For the few custom fonts in DaliFonts only the characters
from _MORPH_CHARS are available.

Demo/Test:
./morph.py
"""

import logging
import time

from typing import List, Dict, Tuple

from PIL import Image


def _SegementsFromLine(w, scan_line) -> Tuple:
    out = []
    last_set = False
    start = None
    for x, cell in enumerate(scan_line):
        this_set = cell != " "
        if this_set != last_set:
            if this_set:
                start = x
            elif start is not None:
                out.append((start, x))
                start = None
        last_set = this_set
    if not start is None:
        out.append((start, w))
    return tuple(out)


def _LineFromSegements(w, segments, char):
    out = [" "] * w
    for start, end in segments:
        # out[start] = char
        while start < end:
            out[start] = char
            start += 1
    return "".join(out)


def _GetNthSegement(scanline, n, w) -> Tuple[int, int]:
    if not scanline:
        return int(w / 2), int(w / 2)
    if len(scanline) <= n:
        # return (w /2, w/2)
        return scanline[-1]
    return scanline[n]


class SegmentedImage:
    """A segment is a horizontal uninterrupted line of set pixels in a bitmap.
    A segmented image consists of a list of segments for each row in the bitmap.
    """

    def __init__(self, img=None):
        if img is not None:
            self._w = len(img[0])
            self._h = len(img)
            self._segments = tuple(
                [_SegementsFromLine(self._w, row) for row in img])

    def __str__(self):
        return " SegmentedImage [%dx%d]: %s" % (self._w, self._h, self._segments)

    def get_size(self) -> Tuple[int, int]:
        return self._w, self._h

    def ToImage(self, marker):
        assert self._segments is not None
        return [_LineFromSegements(self._w, segs, marker) for segs in self._segments]

    def ToImageData(self) -> bytes:
        """Can be used to create a PIL.Image like so
          img = Image.new("1", seg.get_size())
          img.putdata(seg.ToImageData())
        """
        data = bytearray(self._w * self._h)
        w = self._w
        for y, segs in enumerate(self._segments):
            x = 0
            for start, end in segs:
                # print (start, end)
                while x < start:
                    data[y * w + x] = 0
                    x += 1
                while x < end:
                    # print (x, y, w)
                    data[y * w + x] = 1
                    x += 1
            while x < w:
                data[y * w + x] = 0
                x += 1
        return data

    def Merge(self, other: "SegmentedImage", frac: float):
        """Merges this with another Segmented image.
            frac is a number from [0:1] indicating how much each input
            is weighted:  0.0 = only self, 1.0 = only other
        """
        assert 0.0 <= frac <= 1.0, frac
        assert self.get_size() == other.get_size()
        result = SegmentedImage()
        result._w, result._h = self.get_size()
        result._segments = []
        for scanline1, scanline2 in zip(self._segments, other._segments):
            scanline = []
            result._segments.append(scanline)
            max_length = max(len(scanline1), len(scanline2))
            for x in range(max_length):
                seg_self = _GetNthSegement(scanline1, x, self._w)
                seg_other = _GetNthSegement(scanline2, x, self._w)
                beg = seg_self[0] + int(frac * (seg_other[0] - seg_self[0]))
                end = seg_self[1] + int(frac * (seg_other[1] - seg_self[1]))
                scanline.append((beg, end))
        return result

# Helpers for parsing xbm iamge/font files.
# The font files are text files that look like:.
# > cat DaliFonts/oneF.xbm
# #define oneF_width 21
# #define oneF_height 35
# static unsigned char oneF_bits[] = {
#  0x00,0x30,0x00,0x00,0x3c,0x00,0x00,0x3f,0x00,0xc0,0x3f,0x00,0xf0,0x3f,0x00,
#  0xfc,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,
#  0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,
#  0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,
#  0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,
#  0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,0x80,0x3f,0x00,
#  0x80,0x3f,0x00,0xc0,0x3f,0x00,0xc0,0x7f,0x00,0xe0,0x7f,0x00,0xfc,0xff,0x03};


def _ExtractBytesFromXbmLine(line):
    if line.endswith("};"):
        line = line[:-2]
    if line.endswith(","):
        line = line[:-1]
    line = line.strip()
    if not line:
        return []
    # print (repr(line))
    return [int(b_str, 0) for b_str in line.split(",")]


def ParseXbmImage(s):
    """TODO
    """
    width = None
    height = None
    row = [[]]
    for line in s.split("\n"):
        if "width" in line:
            assert width is None
            width = int(line.split("width")[1])
            continue
        if "height" in line:
            assert height is None
            height = int(line.split("height")[1])
            continue
        if "bits" in line:
            assert width is not None
            assert height is not None
            # print ("%dx%d" % (width, height))
            continue

        for b in _ExtractBytesFromXbmLine(line):
            r = row[-1]
            if len(r) == width:
                r = []
                row.append(r)

            for i in range(8):
                bit = " " if (b >> i) & 1 == 0 else "*"
                if len(r) == width:
                    break  # skip rest
                r.append(bit)

    # assert len(row) == height, "%d vs %d" % (len(row), height)
    return row


_MORPH_CHARS = {
    ":": "colon",
    "/": "slash",
    "0": "zero",
    "1": "one",
    "2": "two",
    "3": "three",
    "4": "four",
    "5": "five",
    "6": "six",
    "7": "seven",
    "8": "eight",
    "9": "nine"
}


def LoadMorphFont(prefix: str, suffix: str) -> Dict[str, SegmentedImage]:
    """Loads  a custom font for use with DaliClock or DaliString

    There are a few custom fonts designed to look good for the
    morphing algorithm used here. But nothing prevents us from
    using an arbitrary font.
    """
    font = {}
    wMax = 0
    hMax = 0
    for c in _MORPH_CHARS:
        fn = prefix + _MORPH_CHARS[c] + suffix
        logging.info("processing: %s", fn)
        img = ParseXbmImage(open(fn).read())
        font[c] = SegmentedImage(img)
        dim = len(img[0]), len(img)
        logging.info("dimension: %dx%d" % dim)
        if dim[0] > wMax:
            wMax = dim[0]
        if dim[1] > hMax:
            hMax = dim[1]

    empty = [" "] * wMax
    font[" "] = SegmentedImage([empty] * hMax)
    return font, (wMax, hMax)


class DaliString(object):
    """Class for morphing two strings into each other"""

    def __init__(self, font: Dict[str, SegmentedImage], font_dim):
        self._font = font
        self._font_dim = font_dim
        self._morph_cache = {}

    def Morphed(self, c1, c2, step):
        key = (c1, c2, step)
        if key not in self._morph_cache:
            seg1 = self._font[c1]
            seg2 = self._font[c2]
            seg = seg1.Merge(seg2, step)
            w, h = seg.get_size()
            data = seg.ToImageData()

            img = Image.new("1", seg.get_size())
            img.putdata(data)
            self._morph_cache[key] = img
        return self._morph_cache[key]

    def GetBitmapsForStrings(self, t1: str, t2: str, frac: float):
        assert len(t1) == len(t2)
        return [self.Morphed(c1, c2, frac) for c1, c2 in zip(t1, t2)]


class DaliClock(object):
    """Class for morphing the the current time as it advances"""

    def __init__(self, font: Dict[str, SegmentedImage], font_dim, time_fmt="%H:%M:%S"):
        self._dali_string = DaliString(font, font_dim)
        self._time_fmt = time_fmt
        # for avoiding recomputes
        self._last_time_str = ""
        self._last_time_bitmaps = None

    def GetBitmapsForTime(self, secs: float, steps: int, resting: float):
        t1 = time.strftime(self._time_fmt, time.localtime(secs))
        t2 = time.strftime(self._time_fmt, time.localtime(secs + 1.0))
        if t2 == self._last_time_str:
            return self._last_time_bitmaps
        assert len(t1) == len(t2)
        # get the fractional part
        f = secs - int(secs)
        # the animation happens between [0: 1.0 - resting]
        f = f / (1.0 - resting)
        if f > 1.0:
            f = 1.0
        # snap fraction to steps to improve cache utilization
        frac = int(f * steps) / steps
        self._last_time_bitmaps = self._dali_string.GetBitmapsForStrings(t1, t2, frac)
        self._last_time_str = t1
        return self._last_time_bitmaps

if __name__ == "__main__":
    def ImgToAscii(img: Image) -> str:
        w, h = img.size
        data = img.getdata()
        out = []
        for n, x in enumerate(data):
            if n % w == 0:
                out.append("")
            out[-1] += "*" if x else " "
        return "\n".join(out)

    def main():
        """Example use of DaliClock"""
        import os

        cwd = os.path.dirname(__file__)
        font, font_dim = LoadMorphFont(cwd + "/DaliFonts/", "F.xbm")
        print("FONT_DIM", font_dim)
        # return
        clock = DaliClock(font, font_dim)
        while True:
            t = time.time()
            data = clock.GetBitmapsForTime(t, 20, .3)
            print(ImgToAscii(data[-1]))

    main()
