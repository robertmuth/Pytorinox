#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Simple audio library using simpleaudio

Demo/Test: 
./audio_simple.py

Dependencies:
pip3 install simpleaudio
"""


import logging
import os
import simpleaudio


class Audio:

    def __init__(self, files):
        self.samples = {}
        for fn in files:
            basename = os.path.basename(fn)
            key, ext = os.path.splitext(basename)
            logging.info("loading [%s] -> [%s]" % (fn, key))
            self.samples[key] = simpleaudio.WaveObject.from_wave_file(fn)

    def Names(self):
        return self.samples.keys()

    def Play(self, name, blocking=False):
        p = self.samples[name].play()
        if blocking:
            p.wait_done()


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
            time.sleep(2.0)

    main()
