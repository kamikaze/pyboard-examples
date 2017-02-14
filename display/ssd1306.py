import time
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
    CMD_SET_CHARGE_PUMP = const(0x8d)
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

    def __init__(self, spi, dc, cs, rst=None, width=128, height=64, external_vcc=False):
        page_cnt = height // 8
        self.external_vcc = external_vcc
        self.buffer = bytearray(width * page_cnt)
        self.framebuf = framebuf.FrameBuffer(self.buffer, width, height, framebuf.MVLSB)
        # displays with width of 64 pixels are shifted by 32
        self.column_addr = [32 if width == 64 else 0, width - 1 + 32 if width == 64 else width - 1]
        self.page_addr = [0, page_cnt - 1]
        super().__init__(spi, dc, cs, rst, width, height)

    def reset(self):
        self.rst.high()
        time.sleep_ms(1)
        self.rst.low()
        time.sleep_ms(10)
        self.rst.high()

    def init_display(self):
        for cmd in (
            self.CMD_SET_SLEEP_MODE_ON,
            self.CMD_SET_MEM_ADDR_MODE, 0x00,
            self.CMD_SET_DISPLAY_START_LINE,
            self.CMD_SET_SEGMENT_REMAP | 0x01,
            self.CMD_SET_MUX_RATIO, self.height - 1,
            self.CMD_SET_COM_OUT_SCAN_DIR | 0x08,
            self.CMD_SET_DISPLAY_OFFSET, 0x00,
            self.CMD_SET_COM_PINS_HW_CONF, 0x02 if self.height == 32 else 0x12,
            self.CMD_SET_FRONT_CLOCK_DIVIDER_AND_OSCILLATOR_FREQUENCY, 0x80,
            self.CMD_SET_PRECHARGE_PERIOD, 0x22 if self.external_vcc else 0xf1,
            self.CMD_SET_V_COMH_DESELECT_LEVEL, 0x30,
            self.CMD_SET_CONTRAST_CONTROL, 0xff,
            # self.CMD_SET_DISPLAY_MODE_ON,
            self.CMD_SET_DISPLAY_MODE_NORMAL,
            self.CMD_SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            self.CMD_SET_SLEEP_MODE_OFF):
            self.write_cmd(cmd)

    def send_buffer(self):
        for cmd in [self.CMD_SET_COLUMN_ADDRESS, self.column_addr[0], self.column_addr[1], self.CMD_SET_PAGE_ADDRESS,
                    self.page_addr[0], self.page_addr[1]]:
            self.write_cmd(cmd)

        self.write_data(self.buffer)
