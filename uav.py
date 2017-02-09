import struct
from math import atan2, pi

from pyb import delay, Switch, RTC, USB_VCP
from machine import I2C

import display
from display.ssd1322 import SSD1322
from imu.lsm303 import LSM303D


SIGNALS = bytearray(1)
SIGNAL_USR = 0b1

rtc = RTC()
uav = {
    'imu': {
        'north': .0,
        'roll': .0,
        'pitch': .0,
        'yaw': .0
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
        imu = uav['imu']
        uav['pos']['hdg'] = float(data[0])
        imu['roll'] = float(data[1])
        imu['pitch'] = float(data[2])
        imu['yaw'] = float(data[3])


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


def render_gps_screen(framebuf, uav):
    north = uav['imu']['north']
    pos = uav['pos']
    w = int(north / 2)

    framebuf.fill(0)
    framebuf.text('N: {}'.format(north), 0, 0, 0xF)
    framebuf.text('HDG: {:6.3f}'.format(pos['hdg']), 0, 8, 0xF)
    framebuf.text('ALT: {:6.1f} M'.format(pos['alt']), 0, 16, 0xF)
    framebuf.text('LAT: {:10.6f} {}'.format(pos['lat'], pos['lat_part']), 0, 24, 0xF)
    framebuf.text('LON: {:10.6f} {}'.format(pos['lon'], pos['lon_part']), 0, 32, 0xF)
    framebuf.text('TIME: {}'.format(' '.join(map(str, rtc.datetime()))), 0, 40, 0xF)
    framebuf.fill_rect(127 if w > 0 else 127 + w, 56, abs(w), 8, 0xF)


def render_hud_screen(framebuf, uav):
    imu = uav['imu']
    framebuf.fill(0)
    framebuf.text('ROLL: {}'.format(imu['roll']), 0, 0, 0xF)
    framebuf.text('PITCH: {}'.format(imu['pitch']), 0, 8, 0xF)
    framebuf.text('YAW: {}'.format(imu['yaw']), 0, 16, 0xF)


def switch_cb():
    global SIGNALS
    global SIGNAL_USR

    SIGNALS[0] = SIGNALS[0] | SIGNAL_USR


def run_uav_test(i2c_bus=2):
    global SIGNALS
    global SIGNAL_USR

    SIGNALS[0] = 0
    serial_port = USB_VCP()
    nmea_line = None
    #serial_port.setinterrupt(-1)
    d = display.create_spi_display(SSD1322, 256, 64)
    i2c = I2C(i2c_bus, freq=400000)
    devices = i2c.scan()
    lsm303 = LSM303D(i2c)
    switch = Switch()
    w = 0

    screen_renderers = [render_gps_screen, render_hud_screen]
    renderer_idx = 0
    render_screen = screen_renderers[renderer_idx]

    switch.callback(switch_cb)

    while True:
        # retrieving data
        accel, mag = lsm303.read()

        if serial_port.any():
            nmea_line = str(serial_port.readline(), 'utf-8')

        # processing data
        x, y, z = accel
        x, z, y = mag
        uav['imu']['north'] = atan2(y, x) * 180.0 / pi

        if nmea_line:
            update_gps_data(nmea_line)
            nmea_line = None

        if SIGNALS[0] & SIGNAL_USR:
            renderer_idx = renderer_idx + 1
            render_screen = screen_renderers[renderer_idx % len(screen_renderers)]
            SIGNALS[0] = SIGNALS[0] & ~SIGNAL_USR

        render_screen(d.framebuf, uav)

        d.send_buffer()
        delay(50)

