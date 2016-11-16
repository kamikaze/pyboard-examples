from display.rgb import DisplaySPI


class SSD1322(DisplaySPI):
    CMD_ENABLE_GRAY_SCALE_TABLE = const(0x00)
    CMD_SET_COLUMN_ADDRESS = const(0x15)
    CMD_WRITE_RAM = const(0x5c)
    CMD_READ_RAM = const(0x5d)
    CMD_SET_ROW_ADDRESS = const(0x75)
    CMD_SET_REMAP_AND_DUAL_COM_LINE_MODE = const(0xa0)
    CMD_SET_DISPLAY_START_LINE = const(0xa1)
    CMD_SET_DISPLAY_OFFSET = const(0xa2)
    CMD_SET_DISPLAY_MODE_OFF = const(0xa4)
    CMD_SET_DISPLAY_MODE_ON = const(0xa5)
    CMD_SET_DISPLAY_MODE_NORMAL = const(0xa6)
    CMD_SET_DISPLAY_MODE_INVERSE = const(0xa7)
    CMD_ENABLE_PARTIAL_DISPLAY = const(0xa8)
    CMD_EXIT_PARTIAL_DISPLAY = const(0xa9)
    CMD_SELECT_FUNCTION = const(0xab)
    CMD_SET_SLEEP_MODE_ON = const(0xae)
    CMD_SET_SLEEP_MODE_OFF = const(0xaf)
    CMD_SET_PHASE_LENGTH = const(0xb1)
    CMD_SET_FRONT_CLOCK_DIVIDER_AND_OSCILLATOR_FREQUENCY = const(0xb3)
    CMD_SET_DISPLAY_ENHANCEMENT_A = const(0xb4)
    CMD_SET_GPIO = const(0xb5)
    CMD_SET_SECOND_PRECHARGE_PERIOD = const(0xb6)
    CMD_SET_GRAY_SCALE_TABLE = const(0xb8)
    CMD_SELECT_DEFAULT_LINEAR_GRAY_SCALE_TABLE = const(0xb9)
    CMD_SET_PRECHARGE_VOLTAGE = const(0xbb)
    CMD_SET_V_COMH = const(0xbe)
    CMD_SET_CONTRAST_CURRENT = const(0xc1)
    CMD_MASTER_CONTRAST_CURRENT_CONTROL = const(0xc7)
    CMD_SET_MUX_RATIO = const(0xca)
    CMD_SET_COMMAND_LOCK = const(0xfd)

    _COLUMN_SET = CMD_SET_COLUMN_ADDRESS
    _PAGE_SET = CMD_SET_ROW_ADDRESS
    _RAM_WRITE = CMD_WRITE_RAM
    _RAM_READ = CMD_READ_RAM
    _INIT = (
        (CMD_SET_COMMAND_LOCK, b'\x12'),
        (CMD_SET_FRONT_CLOCK_DIVIDER_AND_OSCILLATOR_FREQUENCY, b'\xd0'),
        (CMD_SET_MUX_RATIO, b'\x3f'),
        (CMD_SET_DISPLAY_OFFSET, b'\x00'),
        (CMD_SET_DISPLAY_START_LINE, b'\x00'),
        (CMD_SET_REMAP_AND_DUAL_COM_LINE_MODE, b'\x14\x11'),
        (CMD_SET_GPIO, b'\x00'),
        (CMD_SELECT_FUNCTION, b'\x01'),
        (CMD_SET_CONTRAST_CURRENT, b'\x7f'),
        (CMD_MASTER_CONTRAST_CURRENT_CONTROL, b'\x0f'),
        (CMD_SELECT_DEFAULT_LINEAR_GRAY_SCALE_TABLE, None),
        (CMD_SET_PHASE_LENGTH, b'\xe2'),
        #(CMD_SET_DISPLAY_ENHANCEMENT_A, b'\xa0\xfd'),
        (CMD_SET_PRECHARGE_VOLTAGE, b'\x1f'),
        (CMD_SET_SECOND_PRECHARGE_PERIOD, b'\x08'),
        (CMD_SET_V_COMH, b'\x07'),

#        (CMD_SET_SLEEP_MODE_ON, None),
        (CMD_SET_DISPLAY_MODE_NORMAL, None),
        (CMD_SET_SLEEP_MODE_OFF, None),
    )


#  displaySend(SEND_CMD, 0xB4); // Display Enhancement A
#  displaySend(SEND_DAT, 0xA0); // = Enable external VSL
#  displaySend(SEND_DAT, 0xB5); // = Normal (reset)

#  displaySenddd(SEND_CMD, 0xD1); // Display Enhancement B
#  displaySend(SEND_DAT, 0xA2); // = Normal (reset)
#  displaySend(SEND_DAT, 0x20); // n/a
    _ENCODE_PIXEL = ">H"
    _ENCODE_POS = ">BB"

    def init(self):
        super().init()
        self.framebuf = bytearray(self.height * self.width // 2)
        #self.fill_ram(b'\x00')

    def fill_buffer(self, value):
        value = 0xF0 & value << 4 ^ 0x0F & value

        for i in range(len(self.framebuf)):
            self.framebuf[i] = value

    def fill_ram(self, value):
        self._write(self.CMD_SET_COLUMN_ADDRESS, b'\x00\x77')
        self._write(self.CMD_SET_ROW_ADDRESS, b'\x00\x40')
        self._write(self.CMD_WRITE_RAM)
        
        for i in range(0x77*0x40):
            self._write(None, value)

    def clear_ram(self):
        self._write(self.CMD_SET_DISPLAY_MODE_OFF)
        self._write(self.CMD_SET_COLUMN_ADDRESS, b'\x00\x77')
        self._write(self.CMD_SET_ROW_ADDRESS, b'\x00\x40')
        self._write(self.CMD_WRITE_RAM)

        for y in range(0x77*0x40):
            self._write(None, b'\x00\x00')
    
        self._write(self.CMD_SET_DISPLAY_MODE_NORMAL)

    def send_buffer(self):
        self._write(self.CMD_SET_COLUMN_ADDRESS, b'\x00\x77')
        self._write(self.CMD_SET_ROW_ADDRESS, b'\x00\x40')
        self._write(self.CMD_WRITE_RAM)

        self._write(None, self.framebuf)

    def send_buffer_one_by_one(self):
        self._write(self.CMD_SET_COLUMN_ADDRESS, b'\x00\x77')
        self._write(self.CMD_SET_ROW_ADDRESS, b'\x00\x40')
        self._write(self.CMD_WRITE_RAM)

        for value in self.framebuf:
            self._write(None, bytes(value))

    def __init__(self, spi, dc, cs, rst=None, width=256, height=64):
        super().__init__(spi, dc, cs, rst, width, height)

