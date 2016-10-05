import os
from pyb import wfi, UART, LED


def parse(line):
    sentence, *data, checksum = line.split(',')

    if sentence == '$GPGGA':
        t, lat, lat_part, lng, lng_part, fix, sat_cnt, hdil, alt, _, geoid_height, _, _  = data

        if fix == '0':
            LED(2).off()
            LED(3).on()
        else:
            LED(3).off()
            LED(2).on()


def log_gps(uart, read_delay=100):
    led = LED(4)
    with open('/sd/gps.log', 'w') as f:
        try:
            while True:
                while uart.any():
                    line = str(uart.readline(), 'utf-8').rstrip()
                    print(line, file=f)
                    #print(line)
                    parse(line)

                f.flush()
                led.toggle()
                wfi()
                #delay(read_delay)
        except KeyboardInterrupt:
            pass

    led.off()
    os.sync()
    LED(1).on()


def run_gps_logger(uart_id, baudrate=9600):
    uart = UART(uart_id, baudrate)
    log_gps(uart, 10)

