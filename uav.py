import struct
from math import atan2, pi

from pyb import delay, RTC, USB_VCP
from machine import I2C

import display
from imu.lsm303 import LSM303D


rtc = RTC()
uav = {
    'imu': {
    },
    'pos': {
        'alt': .0,
        'lat': .0,
        'lat_part': 'N',
        'lon': .0,
        'lon_part': 'E',
        'hdg': .0
    }
}


def process_telemetry(sentence, data, checksum):
    if sentence == '$EXINJ':
        uav['pos']['hdg'] = float(data[0])


def update_gps_data(line):
    try:
        sentence, *data, checksum = line.split(',')
    except ValueError:
        return

    if sentence == '$GPGGA':
        t, lat, lat_part, lon, lon_part, fix, sat_cnt, hdil, alt, _, geoid_height, _, _  = data

        uav['pos']['alt'] = float(alt)
        uav['pos']['lat'] = float(lat) / 100.0
        uav['pos']['lon'] = float(lon) / 100.0
        uav['pos']['lat_part'] = lat_part
        uav['pos']['lon_part'] = lon_part
    elif sentence == '$GPRMC':
        t, _, lat, lat_part, lon, lon_part, speed_over_ground, _, d, _, _ = data

        uav['pos']['lat'] = float(lat) / 100.0
        uav['pos']['lon'] = float(lon) / 100.0
        uav['pos']['lat_part'] = lat_part
        uav['pos']['lon_part'] = lon_part
        dt = ('20'+d[4:6], d[2:4], d[0:2], '1', t[0:2], t[2:4], t[4:6], '0')
        dt = list(map(int, dt))
        rtc.datetime(dt)
    else:
        process_telemetry(sentence, data, checksum)


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
        d.framebuf.fill(0)
        d.framebuf.text('N: {}'.format(h), 0, 0, 0xF)
        pos = uav['pos']
        d.framebuf.text('HDG: {:6.3f}'.format(pos['hdg']), 0, 8, 0xF)
        d.framebuf.text('ALT: {:6.1f} M'.format(pos['alt']), 0, 16, 0xF)
        d.framebuf.text('LAT: {:10.6f} {}'.format(pos['lat'], pos['lat_part']), 0, 24, 0xF)
        d.framebuf.text('LON: {:10.6f} {}'.format(pos['lon'], pos['lon_part']), 0, 32, 0xF)
        d.framebuf.text('TIME: {}'.format(' '.join(map(str, rtc.datetime()))), 0, 40, 0xF)

        w = int(h / 2)

        d.framebuf.fill_rect(127 if w > 0 else 127 + w, 56, abs(w), 8, 0xF)

        d.send_buffer()
        delay(50)

