"""
MIT License

Copyright (c) 2020 IAMLIUBO

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from axp192 import AXP192
import lvgl as lv
from ft63xx import FT6336U
from ili9xxx import ILI9342
from imagetools import get_png_info, open_png


def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class M5Stack(object):
    def __init__(self):
        self.axp = AXP192()
        self.power_on()

        self.lv = lv
        self.lv.init()
        self.disp = ILI9342(self)  # init LCD
        self.touch = FT6336U()  # init TOUCH

        decoder = lv.img.decoder_create()
        decoder.info_cb = get_png_info
        decoder.open_cb = open_png

    def power_on(self):
        # Set GPIO1 & GPIO2 & GPIO4  OD mode
        self.axp.set_gpio_mode(self.axp.GPIO1, self.axp.IO_OPEN_DRAIN_OUTPUT_MODE)
        self.axp.set_gpio_mode(self.axp.GPIO2, self.axp.IO_OPEN_DRAIN_OUTPUT_MODE)
        self.axp.set_gpio_mode(self.axp.GPIO4, self.axp.IO_OPEN_DRAIN_OUTPUT_MODE)

        # Enable GPIO1 Power LED
        self.axp.gpio_write(self.axp.GPIO1, 0)

        # DCDC1 3.3V => ESP32
        self.axp.set_dc_voltage(1, 3.3)
        self.axp.dc_enable(1, 1)

        # DCDC3 3V => LCD Backlight
        self.axp.set_dc_voltage(3, 3)

        # LDO2 3.3V => LCD, SD
        self.axp.set_ldo_voltage(2, 3.3)
        self.axp.ldo_enable(2, 1)

        # LDO3 2V => motor
        self.axp.set_ldo_voltage(3, 2)

        # BAT charge current 190MA
        self.axp.set_bat_charge_current(self.axp.BAT_190MA)

    def lcd_backlight(self, value):
        self.axp.dc_enable(3, value)

    def lcd_brightness(self, value):
        self.axp.set_dc_voltage(3, map(value, 0, 100, 2.4, 3.3))

    def lcd_rst(self, value):
        self.axp.gpio_write(4, value)

    def power_off(self):
        self.axp.power_off()

    def power_led(self, state):
        if state:
            self.axp.gpio_write(self.axp.GPIO1, 0)
        else:
            self.axp.gpio_write(self.axp.GPIO1, 1)

    def vibration(self, state):
        self.axp.ldo_enable(3, state)
