from math import atan2, pi

from pyb import delay, millis, elapsed_millis, Switch, RTC, USB_VCP
from machine import I2C

import display
from display.ssd1322 import SSD1322
from imu.lsm303 import LSM303D


SIGNALS = bytearray(1)
SIGNAL_USR = 0b1

rtc = RTC()
uav = {
    'engines': {
        0: {'throttle': None},
        1: {'throttle': None}
    },
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
    },
    'speed': 0,
    'pid': None,
}


class PID(object):
    def __init__(self, target, kp=.0, ki=.0, kd=.0, windup=20):
        self.target = target
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.cum_error = .0
        self.last_error = .0
        self.windup_guard = windup

    def reset(self):
        self.cum_error = .0
        self.last_error = .0

    def update(self, current_value, dt):
        error = self.target - current_value
        self.cum_error += error * dt

        if self.cum_error < -self.windup_guard:
            self.cum_error = -self.windup_guard
        elif self.cum_error > self.windup_guard:
            self.cum_error = self.windup_guard

        p = self.kp * error
        i = self.ki * self.cum_error
        d = (self.kd * (error - self.last_error) / dt) if dt > 0 else 0

        self.last_error = error

        return p+i+d


def process_telemetry(sentence, data, checksum):
    if sentence == '$EXINJ':
        imu = uav['imu']
        uav['pos']['hdg'] = float(data[0])
        imu['roll'] = float(data[1])
        imu['pitch'] = float(data[2])
        imu['yaw'] = float(data[3])
    elif sentence == '$EXTPID':
        pid = uav['pid']
        pid.kp = float(data[0])
        pid.ki = float(data[1])
        pid.kd = float(data[2])
        pid.reset()


def update_gps_data(line):
    try:
        sentence, *data, checksum = line.split(',')
    except ValueError:
        return

    if sentence == '$GPGGA':
        t, lat, lat_part, lon, lon_part, fix, sat_cnt, hdil, alt, _, geoid_height, _, _ = data

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
        uav['speed'] = int(float(speed_over_ground))
        dt = ('20'+d[4:6], d[2:4], d[0:2], '1', t[0:2], t[2:4], t[4:6], '0')
        dt = list(map(int, dt))
        rtc.datetime(dt)
    else:
        process_telemetry(sentence, data, checksum)


def render_gps_screen(framebuf, uav):
    pos = uav['pos']

    framebuf.fill(0)
    framebuf.text('HDG: {:6.3f}'.format(pos['hdg']), 0, 0, 0xF)
    framebuf.text('ALT: {:6.1f} M'.format(pos['alt']), 0, 8, 0xF)
    framebuf.text('LAT: {:10.6f} {}'.format(pos['lat'], pos['lat_part']), 0, 16, 0xF)
    framebuf.text('LON: {:10.6f} {}'.format(pos['lon'], pos['lon_part']), 0, 24, 0xF)
    framebuf.text('SPEED {:.2f} kts'.format(uav['speed']), 0, 32, 0xF)
    framebuf.text('TIME: {}'.format(' '.join(map(str, rtc.datetime()))), 0, 40, 0xF)


def render_hud_screen(framebuf, uav):
    imu = uav['imu']
    framebuf.fill(0)
    framebuf.text('ROLL: {}'.format(imu['roll']), 0, 0, 0xF)
    framebuf.text('PITCH: {}'.format(imu['pitch']), 0, 8, 0xF)
    framebuf.text('YAW: {}'.format(imu['yaw']), 0, 16, 0xF)


def render_imu_screen(framebuf, uav):
    imu = uav['imu']
    north = imu['north']
    w = int(north / 2)
    framebuf.fill(0)
    framebuf.text('N: {}'.format(north), 0, 0, 0xF)
    framebuf.fill_rect(127 if w > 0 else 127 + w, 56, abs(w), 8, 0xF)


def switch_cb():
    global SIGNALS
    global SIGNAL_USR

    SIGNALS[0] = SIGNALS[0] | SIGNAL_USR


def send_command(serial_port, cmd_id, *data):
    serial_port.write('{},{}\n'.format(cmd_id, *data).encode('ascii'))


def set_engine_throttle(serial_port, engine_id, value):
    engine = uav['engines'][engine_id]

    if engine['throttle'] != value:
        send_command(serial_port, engine_id+1, value)
        engine['throttle'] = value


def adjust_throttle(serial_port, pid_value):
    if pid_value < 0.2:
        pid_value = 0.2
    elif pid_value > 1:
        pid_value = 1

    set_engine_throttle(serial_port, 0, pid_value)
    set_engine_throttle(serial_port, 1, pid_value)


def run_uav_test(i2c_bus=2):
    global SIGNALS
    global SIGNAL_USR

    SIGNALS[0] = 0
    serial_port = USB_VCP()
    nmea_line = None
    # serial_port.setinterrupt(-1)
    disp = display.create_spi_display(SSD1322, 256, 64)
    i2c = I2C(i2c_bus, freq=400000)
    devices = i2c.scan()
    lsm303 = LSM303D(i2c)
    switch = Switch()
    speed_pid = PID(target=500, kp=.4, ki=.2, kd=.1)
    uav['pid'] = speed_pid
    timestamp = None
    w = 0

    screen_renderers = [render_gps_screen, render_hud_screen, render_imu_screen]
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

        # sending orders
        if renderer_idx % 2:
            if timestamp:
                pid_value = speed_pid.update(uav['speed'], elapsed_millis(timestamp) / 1000.0)
                adjust_throttle(serial_port, pid_value)

            timestamp = millis()

        if SIGNALS[0] & SIGNAL_USR:
            renderer_idx = renderer_idx + 1
            render_screen = screen_renderers[renderer_idx % len(screen_renderers)]
            SIGNALS[0] = SIGNALS[0] & ~SIGNAL_USR

        render_screen(disp.framebuf, uav)

        disp.send_buffer()
        delay(50)
