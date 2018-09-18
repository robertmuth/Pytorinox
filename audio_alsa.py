#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Note: does not work equally well on all systems
Simple audio library using audioalsa

Demo/Test: 
./audio_alsa.py

Dependencies:
pip3 install pyalsaaudio
"""

import alsaaudio
import logging
import os
import wave
import threading


class Audio:

    def __init__(self, files):
        self.samples = {}
        self._format = None
        self._device = None
        for fn in files:
            basename = os.path.basename(fn)
            key, ext = os.path.splitext(basename)
            logging.info("loading [%s] -> [%s]" % (fn, key))
            w = wave.open(fn, 'rb')
            param = (w.getnchannels(), w.getframerate(), w.getsampwidth())
            logging.info("params: %s", str(param))
            assert w.getsampwidth() == 2
            if self._format is None:
                self._format = param
            elif self._format != param:
                logging.error("incompatible wave params: %s vs %s",
                              param, self._format)

            self.samples[key] = w.readframes(w.getnframes())
        if self._format:
            self._device = alsaaudio.PCM(
                type=alsaaudio.PCM_PLAYBACK, device="default")
            self._device.setchannels(param[0])
            self._device.setrate(param[1])
            self._device.setperiodsize(param[1] // 8)
            # assume Litte-Endian
            self._device.setformat(alsaaudio.PCM_FORMAT_S16_LE)

    def Names(self):
        return self.samples.keys()

    def _PlayHelper(self, period, s):
        # TODO: consider writing in period chunks rather than everything a once
        self._device.write(s)

    def Play(self, name, blocking=False):
        s = self.samples[name]
        if blocking:
            self._PlayHelper(0, s)
        else:
            threading.Thread(target=self._PlayHelper, args=(0, s)).start()


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
