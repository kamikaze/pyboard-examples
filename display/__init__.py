from machine import SPI, Pin
from display.ssd1322 import SSD1322


def create_display():
    spi = SPI(2, baudrate=20*1024*1024, polarity=0, phase=0)
    dc = Pin('Y2')
    res = Pin('Y1')
    cs = Pin('Y5')
    
    return SSD1322(spi, dc, cs, res, width=256, height=64)

