#!/usr/bin/python3

"""Class for playing simple melodies with the raspi's pwms. 


Demo/Test:
./buzzer.py
"""

import RPi.GPIO as GPIO
import time


class Buzzer(object):

    def __init__(self, pin):
        self._pin = pin
        GPIO.setup(pin, GPIO.OUT)
        self._pwm = GPIO.PWM(pin, 440)
        self._pwm.start(10)

    def playnote(self, freq_hz, duration_ms):
        print(freq_hz, duration_ms)
        if freq_hz > 0:
            self._pwm.ChangeFrequency(freq_hz)
        time.sleep(duration_ms * 1000.0)
        if freq_hz > 0:
            pass
            # self._pwm.stop(volume)

    def playsong(self, notes):
        for note in notes:
            self.playnote(*note)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)

    # generated with midi.py from Midi/fuer_elise.mid
    _FUER_ELISE = [
        (659.255, 240),
        (622.254, 240),
        (659.255, 240),
        (622.254, 240),
        (659.255, 240),
        (493.883, 240),
        (587.330, 240),
        (523.251, 240),
        (440.000, 720),
        (261.626, 240),
        (329.628, 240),
        (440.000, 240),
        (493.883, 720),
        (329.628, 240),
        (415.305, 240),
        (493.883, 240),
        (523.251, 720),
        (329.628, 240),
        (659.255, 240),
        (622.254, 240),
        (659.255, 240),
        (622.254, 240),
        (659.255, 240),
        (493.883, 240),
        (587.330, 240),
        (523.251, 240),
        (440.000, 720),
        (261.626, 240),
        (329.628, 240),
        (440.000, 240),
        (493.883, 720),
        (329.628, 240),
        (523.251, 240),
        (493.883, 240),
        (440.000, 720),
    ]

    buzzer = Buzzer(12)
    buzzer.playnote(440, 1000)
    buzzer.playnote(880, 1000)
    buzzer.playnote(1760, 1000)

    buzzer.playsong(_FUER_ELISE)
    GPIO.cleanup()
