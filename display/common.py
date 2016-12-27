import time


class Display:
    _INIT = ()

    def __init__(self, width, height):
        self.width = width
        self.height = height

        for command, data in self._INIT:
            self.write(command, data)
    
    def readfrom(self, file, direct=True):
        raise NotImplementedError


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
        time.sleep_ms(100)
        self.rst.value(0)
        time.sleep_ms(400)
        self.rst.value(1)
        time.sleep_ms(50)

    def write(self, command=None, data=None):
        if command is not None:
            self.dc.value(0)
            self.cs.value(0)
            self.spi.write(bytearray([command]))
            self.cs.value(1)

        if data is not None:
            self.dc.value(1)
            self.cs.value(0)
            self.spi.write(data)
            self.cs.value(1)

