import framebuf

from display.common import DisplaySPI


class SSD1306(DisplaySPI):
    CMD_SET_LOWER_COLUMN_START_ADDR = const(0x00)
    CMD_SET_HIGHER_COLUMN_START_ADDR = (0x10)
    CMD_SET_MEM_ADDR_MODE = const(0x20)
    CMD_SET_COLUMN_ADDRESS = const(0x21)
    CMD_SET_PAGE_ADDRESS = const(0x22)
    CMD_SET_DISPLAY_START_LINE = const(0x40)
    CMD_SET_CONTRAST_CONTROL = const(0x81)
    #CMD_SET_CHARGE_PUMP = const(0x8d)
    CMD_SET_SEGMENT_REMAP = const(0xa0)
    CMD_SET_DISPLAY_MODE_OFF = const(0xa4)
    CMD_SET_DISPLAY_MODE_ON = const(0xa5)
    CMD_SET_DISPLAY_MODE_NORMAL = const(0xa6)
    CMD_SET_DISPLAY_MODE_INVERSE = const(0xa7)
    CMD_SET_MUX_RATIO = const(0xa8)
    CMD_SET_SLEEP_MODE_ON = const(0xae)
    CMD_SET_SLEEP_MODE_OFF = const(0xaf)
    CMD_SET_COM_OUT_SCAN_DIR = const(0xc0)
    CMD_SET_DISPLAY_OFFSET = const(0xd3)
    CMD_SET_FRONT_CLOCK_DIVIDER_AND_OSCILLATOR_FREQUENCY = const(0xd5)
    CMD_SET_PRECHARGE_PERIOD = const(0xd9)
    CMD_SET_COM_PINS_HW_CONF = const(0xda)
    CMD_SET_V_COMH_DESELECT_LEVEL = const(0xdb)
    CMD_NOP = const(0xe3)

    _INIT = (
        (CMD_SET_DISPLAY_MODE_OFF, None),
        (CMD_SET_MEM_ADDR_MODE, b'\x00'),
        (CMD_SET_DISPLAY_START_LINE, None),
        (CMD_SET_SEGMENT_REMAP | 0x01, None),
        (CMD_SET_MUX_RATIO, b'\x3f'),
        (CMD_SET_COM_OUT_SCAN_DIR | 0x08, None),
        (CMD_SET_DISPLAY_OFFSET, b'\x00'),
        (CMD_SET_COM_PINS_HW_CONF, b'\x12'),
        (CMD_SET_FRONT_CLOCK_DIVIDER_AND_OSCILLATOR_FREQUENCY, b'\x80'),
        (CMD_SET_PRECHARGE_PERIOD, b'\xf1'),
        (CMD_SET_V_COMH_DESELECT_LEVEL, b'\x30'),
        (CMD_SET_CONTRAST_CONTROL, b'\xff'),
        (CMD_SET_DISPLAY_MODE_ON, None),
        (CMD_SET_DISPLAY_MODE_NORMAL, None),
        (CMD_SET_SLEEP_MODE_OFF, None),
    )

    def __init__(self, spi, dc, cs, rst=None, width=128, height=64):
        page_cnt = height // 8
        self.buffer = bytearray(width * page_cnt)
        self.framebuf = framebuf.FrameBuffer(self.buffer, width, height, framebuf.MVLSB)
        self.column_addr = bytes([32 if width == 64 else 0, width - 1 + 32 if width == 64 else width - 1]) # displays with width of 64 pixels are shifted by 32
        self.page_addr = bytes([0, page_cnt - 1])
        super().__init__(spi, dc, cs, rst, width, height)
        self.send_buffer()

    def send_buffer(self):
        self.write(self.CMD_SET_COLUMN_ADDRESS, self.column_addr)
        self.write(self.CMD_SET_PAGE_ADDRESS, self.page_addr)

        self.write(None, self.buffer)

