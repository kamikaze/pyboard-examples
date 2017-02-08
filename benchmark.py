import pyb

import display
from display.ssd1322 import SSD1322


def send_buffer(disp, n=1000):
   disp.framebuf.fill(0)
   start = pyb.millis()

   for i in range(n):
       disp.send_buffer()

   return pyb.elapsed_millis(start)


def text_screen(disp, n=1000):
    disp.framebuf.fill(0)
    start = pyb.millis()

    for i in range(n):
        disp.framebuf.fill(0)

        for y in range(64 // 8):
            disp.framebuf.text('BENCHMARK', 0, y*8, 0xF)

        disp.send_buffer()

    return pyb.elapsed_millis(start)


def run_display_benchmark(disp=None):
    disp = display.create_spi_display(SSD1322, 256, 64)
    
    t1 = send_buffer(disp)
    t2 = text_screen(disp)

    print(t1, t2)

