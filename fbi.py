#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Framebuffer Image Viewer
"""

import sys

from framebuffer import Framebuffer
from PIL import Image


if __name__ == "__main__":
    fb = Framebuffer(int(sys.argv[1]))
    print (fb)
    image = Image.open(sys.argv[2]).convert(mode="RGB")
    image.thumbnail(fb.size)
    print (image, image.mode)

    target = Image.new(mode="RGB", size=fb.size)
    assert image.size <= target.size
    box = ((target.size[0] - image.size[0]) // 2,
           (target.size[1] - image.size[1]) // 2)
    target.paste(image, box)
    fb.show(target)
