import pyb
import display


def run_animation(display, start=0, end=10, step=1, delay=10, from_sd=False):
    while True:
        for i in range(start, end, step):
            with open('{0}/frames/anim_{1:05d}.gray'.format('/sd' if from_sd else '/flash', i), 'rb') as f:
                f.readinto(display.buffer)
                pyb.delay(delay)
                display.send_buffer()


def run_test(from_sd=False):
    d = display.create_display()
    run_animation(d, end=248, from_sd=from_sd)


def run_test_from_flash():
    run_test()


def run_test_from_sd():
    run_test(from_sd=True)

