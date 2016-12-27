from machine import I2C, SPI
import display

disp = display.create_display()
i2c = I2C(2, freq=400000)

devices = i2c.scan()


