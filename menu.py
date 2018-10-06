#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple menu helper for managing a menu and rendering it to an Image.

Demo/Test:
./menu,py
"""


from PIL import Image, ImageDraw, ImageFont


def _RenderFullMenu(font, line_w, line_h, entries):
    out = Image.new("1", (line_w, line_h * (1 + len(entries))))
    draw = ImageDraw.Draw(out)
    for n, e in enumerate(entries):
        draw.text((1, n * line_h), e,  fill="white", font=font)
    # print("FULL", out.size)
    return out


class Menu(object):
    """Simple menu helper
    `font`: font to draw the menu enriess with
    'num_rows`: how many rows are visible
    `line_w', `line_h`: dimension of each row
    `entries`: text of menu entries to be show - add space to end to avoid drawing bug
    `y_offset`: font dependent fudge offset. Try small integers starting with zero.

    """

    def __init__(self, font, num_rows, line_w, line_h, entries, active_entry_index, y_offset=0):
        self._font = font
        self._num_rows = num_rows
        self._line_w = line_w
        self._line_h = line_h
        self.entries = entries
        self._y_offset = y_offset
        # Prerender the menu as if we have unlimited rows
        self._full_menu = _RenderFullMenu(font, line_w, line_h, entries)

    def _lineToEntryIndex(self, active_index, n):
        start = (int(active_index) // self._num_rows) * self._num_rows
        return n + start

    def _ActiveLine(self):
        return self.active_entry_index % self._num_rows

    def draw(self, active_index: float, canvas: ImageDraw):
        """Draw the menu into a canvas.
        `active_index` can be a float for smooth transitions
        """
        # copy the relevant part of the pre-rendered menu
        y_start = self._y_offset + \
            self._lineToEntryIndex(active_index, 0) * self._line_h
        rect = (0, y_start,
                self._line_w, y_start + self._num_rows * self._line_h)
        visible = self._full_menu.crop(rect)
        canvas.bitmap((0, 0), visible, fill="white")
        # then draw the active menu frame
        n = active_index % self._num_rows
        canvas.rectangle((0, int(n * self._line_h),
                          self._line_w - 1,
                          int((n + 1) * self._line_h - 1)),
                         outline="white")


class MenuCentered(object):
    """Simple menu helper
    `font`: font to draw the menu enriess with
    'num_rows`: how many rows are visible - must be odd
    `line_w', `line_h`: dimension of each row
    `entries`: text of menu entries to be show - add space to end to avoid drawing bug
    `y_center' center y coordinate of the screen
    `y_offset`: font dependent fudge offset. Try small integers starting with zero.
    """

    def __init__(self, font, num_rows, line_w, line_h, entries, active_entry_index, y_center, y_offset):
        assert num_rows & 1 == 1
        self._font = font
        self._num_rows = num_rows
        self._line_w = line_w
        self._line_h = line_h
        self.entries = entries
        self._y_offset = y_offset
        self._y_center = y_center
        # Prerender the menu as if we have unlimited rows
        self._full_menu = _RenderFullMenu(font, line_w, line_h, entries)

    def _lineToEntryIndex(self, n):
        start = (self.active_entry_index // self._num_rows) * self._num_rows
        return n + start

    def draw(self, active_index: float, canvas: ImageDraw):
        """Draw the menu into a canvas.
        `active_index` can be a float for smooth transitions
        """
        # copy the relevant part of the pre-rendered menu
        y_middle = int(active_index * self._line_h + self._line_h // 2)
        y_start = int((active_index - self._num_rows // 2) * self._line_h)
        y_end = int((active_index + 1 + self._num_rows // 2) * self._line_h)
        rect = (0, self._y_offset + y_start,
                self._line_w, self._y_offset + y_end)
        visible = self._full_menu.crop(rect)
        canvas.bitmap((0, self._y_center - (y_middle - y_start)),
                      visible, fill="white")
        # then draw the active menu frame
        canvas.rectangle((0, self._y_center - 1 - self._line_h // 2,
                          self._line_w - 1, self._y_center + 1 + self._line_h // 2),
                         outline="white")


if __name__ == "__main__":
    import time
    import os

    def ImgToAscii(img: Image) -> str:
        w, h = img.size
        data = img.getdata()
        out = []
        for n, x in enumerate(data):
            if n % w == 0:
                out.append("")
            out[-1] += "*" if x else " "
        return "\n".join(out)

    _ENTRIES = [
        "00 zero ",
        "01 one ",
        "02 two",
        "03 three ",
        "04 four ",
        "05 five ",
        "06 six ",
        "07 seven ",
        "08 eight ",
        "09 nine ",
        "10 ten ",
        "11 elven ",
        "12 twelve ",
    ]

    H = 64
    W = 128
    FONT_H = 16
    cwd = os.path.dirname(__file__)
    FONT = ImageFont.truetype(cwd + "/Fonts/code2000.ttf", FONT_H)
    #menu = Menu(FONT, H // FONT_H, W,  FONT_H, _ENTRIES, 0, 3)
    menu = MenuCentered(FONT, H // FONT_H - 1, W,  FONT_H, _ENTRIES, 0, 32, 3)
    image = Image.new("1", (W, H))
    draw = ImageDraw.Draw(image)
    r = range(len(menu.entries) * 4)
    r = list(r) + list(reversed(r))
    r = [x / 4 for x in r]
    for i in r:
        draw.rectangle((0, 0, W, H), "black")
        menu.draw(i, draw)
        print ("\n" * 100)
        print(ImgToAscii(image))
        time.sleep(.25)
