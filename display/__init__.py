import time


class Display:
    _INIT = ()

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.framebuf = bytearray(width * height)

        for command, data in self._INIT:
            self.write(command, data)


class DisplaySPI(Display):
    def __init__(self, spi, dc, cs, rst=None, width=1, height=1):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)

        if self.rst:
            self.rst.init(self.rst.OUT, value=0)
            self.reset()

        super().__init__(width, height)

    def reset(self):
        self.rst.low()
        time.sleep_ms(50)
        self.rst.high()
        time.sleep_ms(50)

    def write(self, command=None, data=None):
        if command is not None:
            self.dc.low()
            self.cs.low()
            self.spi.write(bytearray([command]))
            self.cs.high()

        if data is not None:
            self.dc.high()
            self.cs.low()
            self.spi.write(data)
            self.cs.high()

    def read(self, command=None, count=0):
        self.dc.low()
        self.cs.low()

        if command is not None:
            self.spi.write(bytearray([command]))

        if count:
            data = self.spi.read(count)

        self.cs.high()

        return data

