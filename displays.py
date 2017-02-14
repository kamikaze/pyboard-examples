import pyb
import display
from random import choice
from display.ssd1322 import SSD1322
from display.ssd1306 import SSD1306


def run_ssd1306_test(delay=400, from_sd=True):
    d = display.create_spi_display(SSD1306, 128, 64)
    ids = [1,2,3]

    while True:
        with open('{0}/frames/natenchik{1}.gray'.format('/sd' if from_sd else '/flash', choice(ids)), 'rb') as f:
            f.readinto(d.buffer)
            pyb.delay(delay)
            d.send_buffer()


def run_ssd1322_test():
    d = display.create_spi_display(SSD1322, 256, 64)

    return d
