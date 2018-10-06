## About

Pytorinox is a collection of single file helpers written in Python3.

It is mostly aimed at the Raspberry Pi platform but some components should
work with MicroPython on platform like an ESP32 with minor modifications.

Pytorinox is **not** a traditional Python library and there is **no** `setup.py`.
It should be sufficient to copy or symlink the helper files you need
into the directory with your main application.

Most helper files can be run as a test which also demonstrates
how to use them. Additional documentation can found on 
[Robert's Real-Simple Raspi Resources](https://raspi.muth.org/) site.

## Helper Overview

* audio_alsa.py  - play back wav sounds via alsa lib

* audio_simple.py  - play back wav sounds via simpleaudio lib

* audio_aplay.py - play back wave sound via external tool (`aplay`)

* bme280.py - read temperature, humidity and pressure from bme280 sensor (i2c)

* buzzer.py  - play simple melodies via pwm

* fbi.py - frame buffer image viewer tool (simple demo of framebuffer.py) 

* framebuffer.py - render an Image into a linux framebuffer device

* l3g4200d.py - 3 axis gyroscope (i2c)

* midi.py - extract simple melodies from midi files for use with buzzer.py 

* menu.py - scrollable menus rendered into an Image 

* morph.py - dali clock style text morphing 

* rotary_encoder.py - decoder for rotary encoder switches

* spi_display.py - render an image on an SPI display (supports several OLED, TFT and E-Ink drivers)   

* ttp229.py - capacitive touch sensor (i2c)

* tts.py - text-to-speech via external tools (`pico2wave`, `aplay`)


## License

All code is governed by LICENSE.txt (GPL 3) unless otherwise noted.
For alternative licensing please contact the author.


* DaliFont/* files are from: http://www.jwz.org/xdaliclock/
* Fonts/code2000.ttf is unrestricted share ware (https://en.wikipedia.org/wiki/Code2000)
* Sounds/* are public domain from various sources

## Dependencies

All helper files are stand-alone, meaning they do not depend
on other helpers.

Some helper may depend on certain base libraries like 

* [Image](https://pillow.readthedocs.io)
* [GPIO](https://pypi.org/project/RPi.GPIO/)
* [smbus](https://pypi.org/project/smbus2/)
* [evdev](https://python-evdev.readthedocs.io)

and standard tools like 

* aplay
* pico2wave
  
## Author

robert@muth.org


