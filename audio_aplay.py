#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple audio library using the external aplay binary

Demo/Test: 
./audio_aplay.py Sounds/*

Dependencies
sudo apt install alsa-utils
"""


import logging
import os


class Audio(object):
    def __init__(self, files):
        self.samples = {}
        for fn in files:
            basename = os.path.basename(fn)
            key, ext = os.path.splitext(basename)
            logging.info("loading [%s] -> [%s]" % (fn, key))
            self.samples[key] = fn

    def Names(self):
        return self.samples.keys()

    def Play(self, name, blocking):
        s = self.samples[name]
        logging.info("playing [%s]" % s)
        if blocking:
            os.system("aplay '%s'" % s)
        else:
            os.spawnlp(os.P_NOWAIT, "aplay", "aplay", s)


if __name__ == "__main__":
    import time
    import glob

    def main():
        logging.basicConfig(level=logging.INFO)
        cwd = os.path.dirname(__file__)
        audio = Audio(glob.glob(cwd + "/Sounds/*.wav"))
        for n in audio.Names():
            logging.info("play %s" % n)
            audio.Play(n, True)
            time.sleep(1.0)

    main()
