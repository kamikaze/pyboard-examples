import time


class Display:
    _INIT = ()

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.reset()
        self.init_display()
        self.send_buffer()
    
    def readfrom(self, file, direct=True):
        raise NotImplementedError

    def reset(self):
        pass

    def init_display(self):
        pass

    def send_buffer(self):
        pass


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

        super().__init__(width, height)

    def write_cmd(self, cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def write_data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)

    def write(self, cmd=None, data=None):
        if cmd is not None:
            self.write_cmd(cmd)

        if data is not None:
            self.write_data(data)
