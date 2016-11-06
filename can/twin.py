from pyb import CAN, delay


def init_cans():
    can1 = CAN(1, CAN.NORMAL)
    can2 = CAN(2, CAN.NORMAL)
    can1.setfilter(0, CAN.LIST16, 0, (23, 24, 25, 26))
    can1.setfilter(1, CAN.LIST16, 1, (33, 34, 35, 36))

    return can1, can2


def twin_test(receiver, sender, delay_ms=500):
    while True:
        sender.send(b'1234', 23, timeout=10000)

        data = receiver.recv(0, timeout=10000)

        print(data)

        delay(delay_ms)


def run_twin_test(delay_ms=500):
    can1, can2 = init_cans()
    twin_test(can1, can2, delay_ms)

