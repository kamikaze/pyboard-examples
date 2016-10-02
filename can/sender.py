from pyb import CAN, LED, delay
from urandom import randint
from time import ticks_us, ticks_diff


#def cb10(bus, reason):
#    print('cb1_0', bus, reason)


#def cb11(bus, reason):
#    print('cb1_1', bus, reason)


#def cb2(bus, reason):
#    print('cb2', bus, reason)


def init_cans():
    can1 = CAN(1, CAN.NORMAL)
    can2 = CAN(2, CAN.NORMAL)
    can1.setfilter(0, CAN.LIST16, 0, (23, 24, 25, 26))
    can1.setfilter(1, CAN.LIST16, 1, (33, 34, 35, 36))


#    can1.rxcallback(0, cb10)
#    can1.rxcallback(1, cb11)

#    can2.rxcallback(0, cb2)
#    can2.rxcallback(1, cb2)

    return can1, can2


def led_disco(can, leds, delay_ms=500):
    max_led_id = len(leds) - 1

    while True:
        led_id = randint(0, max_led_id)
        state = randint(0, 1)

        if state:
            leds[led_id].on()
        else:
            leds[led_id].off()

        can.send(state << 2 | led_id, 11, timeout=10000)
        delay(delay_ms)


def run_led_disco(delay_ms=500):
    leds = [LED(1), LED(2), LED(3), LED(4)]
    _, can2 = init_cans()
    led_disco(can2, leds, delay_ms)


def benchmark(max_iter_cnt = 100, frame_size = 128):
    payload = '12345678'
    _id = 12#3

    can1, can2 = init_cans()
    start = ticks_us()

    for iter_cnt in range(max_iter_cnt):
        can2.send(payload, _id, timeout=1000)
        # can1.recv(0)

    diff = ticks_diff(start, ticks_us())
    diff_sec = diff / 1000000.0
    data_kbits = len(payload) * (iter_cnt + 1.0) * 8.0 / 1000.0
    frame_kbits = frame_size * (iter_cnt + 1.0) * 8.0 / 1000.0
    data_speed = data_kbits / diff_sec
    frame_speed = frame_kbits / diff_sec
    frame_rate = (iter_cnt + 1.0) / diff_sec

    print('Payload {0} has been sent {1} times in {2}s at {3} kbps'.format(payload, iter_cnt + 1, diff_sec, data_speed))
    print('CAN frame (~{0} bits) has been sent {1} times in {2}s at {3} fps / {4} kbps'.format(frame_size, iter_cnt + 1, diff_sec, frame_rate, frame_speed))

