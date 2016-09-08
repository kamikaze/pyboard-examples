import os
from pyb import CAN, rng, delay, disable_irq, enable_irq
from can import init_cans


flags = 0b00000000



def cb10(bus, reason):
    global flags
    print('cb1_0', bus, reason)

    print('Setting FIFO 1 flag')
    flags |= 1

    print('Exiting cb1_0')


def cb11(bus, reason):
    global flags
    print('cb1_1', bus, reason)

    print('Setting FIFO 2 flag')
    flags |= 2

    print('Exiting cb1_1')


def run_logger_test(max_iter_count=1000):
    global flags
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
            print('Data sent, Delaying...')
            delay(20)
            print('Woke up')

            print('Disbling IRQs')
            irq_state = disable_irq()

            if flags & 1:
                print('FIFO 1')
                while can1.any(0):
                    data = can1.recv(0)
                    print(data)
                    print(*data, sep=',', file=f1)

                flags &= ~1

            enable_irq(irq_state)
            print('Enabled IRQs')

            delay(5)

            print('Disbling IRQs')
            irq_state = disable_irq()

            if flags & 2:
                print('FIFO 2')
                while can1.any(1):
                    data = can1.recv(1)
                    print(data)
                    print(*data, sep=',', file=f1)

                flags &= ~2

            enable_irq(irq_state)
            print('Enabled IRQs')

        while can1.any(0):
            print('Receiving data')
            data = can1.recv(0)
            print(data)
            print(*data, sep=',', file=f1)
        
        while can1.any(1):
            print('Receiving data')
            data = can1.recv(1)
            print(data)
            print(*data, sep=',', file=f1)
            

    os.sync()

