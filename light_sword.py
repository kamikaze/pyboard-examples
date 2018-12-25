import gc
import pyb

from ws2813 import WS2813

PATTERN_SWITCH = False


def wheel(pos):
    if pos < 85:
        return (pos*3, 255-pos*3, 0)
    elif pos < 170:
        pos -= 85

        return (255-pos*3, 0, pos*3)
    else:
        pos -= 170

        return (0, pos*3, 255-pos*3)


def rainbow_flow(led_strip, data, wait_ms=50):
    global PATTERN_SWITCH
    led_count = len(data)

    for j in range(256):
        for q in range(3):
            for i in range(0, led_count, 3):
                if PATTERN_SWITCH:
                    raise StopIteration

                data[i+q] = wheel((i+j) % 255)

            led_strip.show(data)
            pyb.delay(wait_ms)


def rainbow_glow(led_strip, data, wait_ms=50):
    led_count = len(data)
    rgb = [255, 0, 0]

    for dec_color in range(3):
        inc_color = 0 if dec_color == 2 else dec_color + 1

        for j in range(255):
            rgb[dec_color] -= 1
            rgb[inc_color] += 1

            for i in range(led_count):
                if PATTERN_SWITCH:
                    raise StopIteration

                data[i] = (rgb[0], rgb[1], rgb[2])
            
            led_strip.show(data)
            pyb.delay(wait_ms)


def pattern_rainbow_flow(led_strips, data, wait_ms=50):
    while True:
        for led_strip in led_strips:
            rainbow_flow(led_strip, data, wait_ms)

        gc.collect()


def pattern_rainbow_glow(led_strips, data, wait_ms=50):
    while True:
        for led_strip in led_strips:
            rainbow_glow(led_strip, data, wait_ms)

        gc.collect()


def shift_pattern_func():
    global PATTERN_SWITCH

    PATTERN_SWITCH = True


def run_light_sword_test(spi_bus=1, led_count=30, wait_ms=50):
    global PATTERN_SWITCH

    sw = pyb.Switch()

    led_strip_count = 1
    led_strips = tuple(WS2813(1, 64) for _ in range(led_strip_count))

    pattern_funcs = (
        pattern_rainbow_flow,
        pattern_rainbow_glow,
    )

    pattern_idx = -1
    pattern_func_cnt = len(pattern_funcs)
    data = [(0, 0, 0,)] * led_count

    sw.callback(shift_pattern_func)

    try:
        while True:
            PATTERN_SWITCH = False
            pattern_idx += 1
            pattern_func = pattern_funcs[pattern_idx % pattern_func_cnt]

            try:
                pattern_func(led_strips, data, wait_ms)
            except StopIteration:
                pass

            gc.collect()
    except KeyboardInterrupt:
        print('Disabling switch callback')
        sw.callback(None)

