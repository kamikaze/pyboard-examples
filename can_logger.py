import os
from mutex import Mutex
from pyb import CAN, rng
from can import init_cans


flag_mutex = Mutex()
flags = 0b00000000



def cb10(bus, reason):
    global flags, flag_mutex
    print('cb1_0', bus, reason)

    if flag_mutex.test():
        print('Setting FIFO 1 flag')
        flags |= 1

    print('Exiting cb1_0')


def cb11(bus, reason):
    global flags, flag_mutex
    print('cb1_1', bus, reason)

    if flag_mutex.test():
        print('Setting FIFO 2 flag')
        flags |= 2

    print('Exiting cb1_1')


def run_logger_test(max_iter_count=1000):
    global flags, flag_mutex
    can1, can2 = init_cans()

    can1.rxcallback(0, cb10)
    can1.rxcallback(1, cb11)

    ids = (113, 123,)
    _id = None

    with open('/sd/can1.log', 'w') as f1, open('/sd/can2.log', 'w') as f2:
        for i in range(max_iter_count):
            data = '12345'

            _id = ids[rng() % len(ids)]
            print('Writing to CAN2: ', _id, data)
            print(_id, data, sep=',', file=f2)
            can2.send(data, _id)

            with flag_mutex:
                print('Entered mutex')
                if flags & 1:
                    print('FIFO 1')
                    while can1.any(0):
                        data = can1.recv(0)
                        print(data)
                        print(*data, sep=',', file=f1)

                    flags &= ~1

            with flag_mutex:
                print('Entered mutex')
                if flags & 2:
                    print('FIFO 2')
                    while can1.any(1):
                        data = can1.recv(1)
                        print(data)
                        print(*data, sep=',', file=f1)

                    flags &= ~2

        while can1.any(0):
            data = can1.recv(0)
            print(data)
            print(*data, sep=',', file=f1)
        
        while can1.any(1):
            data = can1.recv(1)
            print(data)
            print(*data, sep=',', file=f1)
            

    os.sync()

