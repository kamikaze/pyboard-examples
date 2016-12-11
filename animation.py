import pyb
import disp


def read_frames(start, end, step=1, from_sd=False):
    for i in range(start, end, step):
        with open('{0}/frames/anim_{1:05d}.gray'.format('/sd' if from_sd else '/flash', i), 'rb') as f:
            yield f.read()


def run_animation(display, start=0, end=10, step=1, delay=50, from_sd=False):
    while True:
        for frame in read_frames(start, end, step, from_sd):
            pyb.delay(delay)
            display.replace_buffer(frame)
            display.send_buffer()


def run_test(from_sd=False):
    d = disp.create_display()
    run_animation(d, end=100, step=10, from_sd=from_sd)

def run_test_from_flash():
    run_test()


def run_test_from_sd():
    run_test(from_sd=True)

