from machine import SPI, Pin
from display import ssd1322


def create_display():
    spi = SPI(1, baudrate=10*1024*1024, polarity=0, phase=0)
    dc = Pin('Y2')
    res = Pin('Y1')
    cs = Pin('X5')
    display = ssd1322.SSD1322(spi, dc, cs, res, width=256, height=64)

    return display

