#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Collection of helpers for text-to-speech output using 
svox pico engine. Language codes:

en-US   English
en-GB   Great 
de-DE   German
es-ES   Spanish
fr-FR   French
it-IT   Italian


Demo/Test: 
./tts.py

Dependencies:
sudo apt install libttspico-utils
sudo apt install alsa-utils
sudo apt install sox
"""
import os


def TextToWave(language, text, filename):
    cmd = "pico2wave --lang=%s --wave=%s  '%s'" % (language, filename, text)
    os.system(cmd.encode("utf-8"))


def ConvertToMono(fileIn, fileOut):
    os.system("sox -G %s  %s channels 1 rate 44100" % (fileIn, fileOut))


def PlayWave(filename):
    os.system("aplay " + filename)


if __name__ == "__main__":
    import time

    CONFIG = [
        ("en-US", "Hello! How are you?"),
        ("en-GB", "Hello! How are you?"),
        ("de-DE", "Hallo! Wie geht es Ihnen"),
        ("es-ES", "¡Hola! ¿Cómo estás?"),
        ("fr-FR", "Salut! Comment allez-vous?"),
        ("it-IT", "Ciao! Come stai?"),
    ]


    def main():
        for lang, sentence in CONFIG:
            print(lang, sentence)
            t = time.time()
            TextToWave(lang, sentence, "/tmp/xxx.wav")
            print("conversion to wave: %.1f msec" %
                  (1000.0 * (time.time() - t)))

            t = time.time()
            ConvertToMono("/tmp/xxx.wav", "/tmp/yyy.wav")
            print("conversion to mono %.1f msec" %
                  (1000.0 * (time.time() - t)))

            t = time.time()
            PlayWave("/tmp/yyy.wav")
            print("playback %.1f msec" % (1000.0 * (time.time() - t)))


    main()
