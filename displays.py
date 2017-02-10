
import display
from display.ssd1322 import SSD1322
from display.ssd1306 import SSD1306


def run_ssd1306_test():
    d = display.create_spi_display(SSD1306, 128, 64)

    return d

