import os
from pyb import delay, UART


def log_gps(uart, read_delay=100):
    with open('/sd/gps.log', 'w') as f:
        try:
            while True:
                while uart.any():
                    line = uart.readline()
                    print(line, file=f)
                    #print(line)
                f.flush()
                delay(read_delay)
        except KeyboardInterrupt:
            pass

    os.sync()


def run_gps_logger(uart_id, baudrate=9600):
    uart = UART(uart_id, baudrate)
    log_gps(uart, 10)

