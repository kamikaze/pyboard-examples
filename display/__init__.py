from machine import SPI, Pin


def create_spi_display(cls, width, height, spi_bus=2, dc_pin='Y2', res_pin='Y1', cs_pin='Y5', baudrate=20*1024*1024, polarity=0, phase=0):
    spi = SPI(spi_bus, baudrate=baudrate, polarity=polarity, phase=phase)
    dc = Pin(dc_pin)
    res = Pin(res_pin)
    cs = Pin(cs_pin)
    
    return cls(spi, dc, cs, res, width=width, height=height)

