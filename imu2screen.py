from math import atan2, pi

from pyb import delay
from machine import I2C

import display
from display.ssd1322 import SSD1322
from imu.lsm303 import LSM303D


def run_imu_test(i2c_bus=2):
    d = display.create_spi_display(SSD1322, 256, 64)
    i2c = I2C(i2c_bus, freq=400000)
    devices = i2c.scan()
    lsm303 = LSM303D(i2c)
    w = 0

    while True:
        accel, mag = lsm303.read()
        x, y, z = accel
        x, z, y = mag

        h = atan2(y, x) * 180.0 / pi

        d.framebuf.fill_rect(0, 0, 128, 8, 0x00)
        d.framebuf.text('N: {}'.format(h), 0, 0, 0x0F)

        d.framebuf.fill_rect(0, 47, w, 8, 0)
        d.framebuf.fill_rect(1, 56, w, 8, 0)

        w = abs(int(h))

        d.framebuf.fill_rect(0, 47, w, 8, 0x0F)
        d.framebuf.fill_rect(1, 56, w, 8, w % 15 + 1)

        d.send_buffer()
        delay(25)

