#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Framebuffer helper that makes lots of simpifying assumptions

bits_per_pixel    assumed memory layout
16                rgb565
24                rgb
32                argb

"""

from PIL import Image


def _read_and_convert_to_ints(filename):
    with open(filename, "r") as fp:
        content = fp.read()
        tokens = content.strip().split(",")
        return [int(t) for t in tokens if t]


def _converter_argb(image: Image):
    return bytes([x for r, g, b in image.getdata() for x in (255, r, g, b)])


def _converter_rgb565(image: Image):
    return bytes([x for r, g, b in image.getdata()
                  for x in ((g & 0x1c) << 3 | (b >> 3),  r & 0xf8 | (g >> 5))])


def _converter_rgb(image: Image):
    return image.tobytes()


_CONVERTER = {
    16: _converter_rgb565,
    24: _converter_rgb,
    32: _converter_argb,
}


class Framebuffer(object):

    def __init__(self, device_no: int):
        self.path = "/dev/fb%d" % device_no
        config_dir = "/sys/class/graphics/fb%d/" % device_no
        self.size = tuple(_read_and_convert_to_ints(
            config_dir + "/virtual_size"))
        self.stride = _read_and_convert_to_ints(config_dir + "/stride")[0]
        self.bits_per_pixel = _read_and_convert_to_ints(
            config_dir + "/bits_per_pixel")[0]
        self._converter = _CONVERTER.get(self.bits_per_pixel)
        assert self._converter is not None
        assert self.stride == self.bits_per_pixel // 8 * self.size[0]

    def __str__(self):
        args = (self.path, self.size, self.stride, self.bits_per_pixel)
        return "%s  size:%s  stride:%s  bits_per_pixel:%s" % args

    # Note: performance is terrible even for medium resolutions
    def show(self, image: Image):
        assert image.mode == "RGB"
        assert image.size == self.size
        out = self._converter(image)
        with open(self.path, "wb") as fp:
            fp.write(out)


if __name__ == "__main__":
    import time
    from PIL import ImageDraw
    for i in range(2):
        fb = Framebuffer(i)
        print (fb)
        image = Image.new("RGB", fb.size)
        draw = ImageDraw.Draw(image)
        draw.rectangle(((0, 0), fb.size), fill="green")
        draw.ellipse(((0, 0), fb.size), fill="blue", outline="red")
        draw.line(((0, 0), fb.size), fill="green", width=2)
        start = time.time()
        for i in range(5):
            fb.show(image)
        stop = time.time()
        print ("fps: %.2f" % (10 / (stop - start)))
