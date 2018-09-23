## About

Pytorinox is a collection of single file helpers written in Python3.

It is mostly aimed at the Raspberry Pi platform but some components should
work with MicroPython on platform like an ESP32 with minor modifications.

Pytorinox is **not** a traditional Python library and there is **no** `setup.py`.
It should be sufficient to copy or symlink the helper files you need
into the directory with your main application.

Most helper file can be run by itself as a test which also demonstrates
how to use it:

* audio_alsa.py  - play back wav sounds via alsa lib

* audio_simple.py  - play back wav sounds via simpleaudio lib

* audio_aplay.py - play back wave sound via external tool (`aplay`)

* bme280.py - read temperature, humidity and pressure from bme280 sensor

* buzzer.py  - play simple melodies via pwm

* fbi.py - frame buffer image viewer tool (simple demo of framebuffer.py) 

* framebuffer.py - render an Image into a linux framebuffer device

* midi.py - extract simple melodies from midi files for use with buzzer.py 

* menu.py - scrollable menus rendered into an Image 

* morph.py - dali clock style text morphing 

* oled.py - render an image on an SPI display (supports several OLED drivers)   

* rotary_encoder.py - decoder for rotary encoder switches

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

Some helper may depend on certain base libraries like `Image`, `GPIO`, `smbus` and 
standard tools like `aplay`, `pico2wave`
  
## Author

robert@muth.org


