from pyb import delay, USB_VCP


def run_usb_vcp_test():
    serial_port = USB_VCP()
    nmea_line = None
    #serial_port.setinterrupt(-1)

    while True:
        # retrieving data
        if serial_port.any():
            nmea_line = str(serial_port.readline(), 'utf-8')

        if nmea_line:
            delay(1)
            nmea_line = None

        delay(50)

