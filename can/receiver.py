import os
from pyb import CAN, LED, disable_irq, enable_irq


SIGNALS = bytearray(1)


def cb10(bus, reason):
    global SIGNALS
    SIGNALS[0] |= 0b1


#def cb11(bus, reason):
#    print('cb1_1', bus, reason)


#def cb2(bus, reason):
#    print('cb2', bus, reason)


def _init_cans():
    can1 = CAN(1, CAN.NORMAL, prescaler=2, sjw=1, bs1=14, bs2=6)
    can2 = CAN(2, CAN.NORMAL, prescaler=2, sjw=1, bs1=14, bs2=6)
    can1.setfilter(0, CAN.LIST16, 0, (11, 12, 13, 14))
    can1.setfilter(1, CAN.LIST16, 1, (21, 22, 23, 24))


    can1.rxcallback(0, cb10)
#    can1.rxcallback(1, cb11)

#    can2.rxcallback(0, cb2)
#    can2.rxcallback(1, cb2)

    return can1, can2


def listen_for_signals(can, leds):
    global SIGNALS
    SIGNALS[0] &= 0b0
    state = None

    with open('/sd/can.log', 'a') as f:
        try:
            while True:
                if SIGNALS[0] & 0b1:
                    state = disable_irq()
                    SIGNALS[0] &= 0b0
                    enable_irq(state)

                    while can.any(0):
                        _id, rtr, fmi, data = can.recv(0, timeout=10000)
                        print(str(_id), '1' if rtr else '0', str(fmi), str(data), sep=',', file=f)
                        #f.flush()
                        data = int.from_bytes(data, 'little')

                        if _id == 11:
                            if data & 0b100:
                                leds[data & 0b11].on()
                            else:
                                leds[data & 0b11].off()
        except Exception as e:
            print('Exception: {}'.format(e))
        except KeyboardInterrupt as e:
            print(e)

    os.sync()


def listen_for_benchmark(can):
    global SIGNALS
    SIGNALS[0] &= 0
    state = None

    while True:
        if SIGNALS[0] & 1:
            state = disable_irq()
            SIGNALS[0] &= 0
            enable_irq(state)

            while can.any(0):
                can.recv(0, timeout=10000)


def run_signal_listener():
    leds = [LED(1), LED(2), LED(3), LED(4)]
    can1, _ = _init_cans()
    listen_for_signals(can1, leds)


def run_benchmark_listener():
    can1, _ = _init_cans()
    listen_for_benchmark(can1)

