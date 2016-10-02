import os


def log(*args):
    with open('/sd/can.log', 'a') as f:
        print(','.join(args), file=f)

    os.sync()

