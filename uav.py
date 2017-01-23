import struct
from math import atan2, pi

from pyb import delay, USB_VCP
from machine import I2C

import display
from imu.lsm303 import LSM303D


uav = {
    'pos': {
        'lat': .0,
        'lon': .0
    }
}


def update_gps_data(line):
    print(line)
    try:
        sentence, *data, checksum = line.split(',')
    except ValueError:
        return

    if sentence == '$GPGGA':
        t, lat, lat_part, lon, lon_part, fix, sat_cnt, hdil, alt, _, geoid_height, _, _  = data
        uav['pos']['lat'] = float(lat) / 100.0
        uav['pos']['lon'] = float(lon) / 100.0


def run_uav_test(i2c_bus=2):
    serial_port = USB_VCP()
    nmea_line = None
    #serial_port.setinterrupt(-1)
    d = display.create_display()
    i2c = I2C(i2c_bus, freq=400000)
    devices = i2c.scan()
    lsm303 = LSM303D(i2c)
    w = 0

    while True:
        # retrieving data
        accel, mag = lsm303.read()

        if serial_port.any():
            nmea_line = str(serial_port.readline(), 'utf-8')

        # processing data
        x, y, z = accel
        x, z, y = mag
        h = atan2(y, x) * 180.0 / pi

        if nmea_line:
            update_gps_data(nmea_line)
            nmea_line = None

        # displaying data
        d.framebuf.fill_rect(0, 0, 128, 24, 0x00)
        d.framebuf.text('N: {}'.format(h), 0, 0, 0x0F)
        d.framebuf.text('LAT: {:9.6f}'.format(uav['pos']['lat']), 0, 8, 0xF)
        d.framebuf.text('LON: {:9.6f}'.format(uav['pos']['lon']), 0, 16, 0xF)

        d.framebuf.fill_rect(127 if w > 0 else 127 + w, 56, abs(w), 8, 0)

        w = int(h / 2)

        d.framebuf.fill_rect(127 if w > 0 else 127 + w, 56, abs(w), 8, 0x0F)

        d.send_buffer()
        delay(25)

