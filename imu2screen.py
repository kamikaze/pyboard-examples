from machine import I2C, SPI
import display


LSM303_ADDRESS_ACCEL = 0x32 >> 1
LSM303_ADDRESS_MAG = 0x3C >> 1
 
LSM303_REGISTER_ACCEL_CTRL_REG1_A = 0x20
LSM303_REGISTER_MAG_MR_REG_M = 0x02
LSM303_REGISTER_MAG_OUT_X_H_M = 0x03
LSM303_REGISTER_ACCEL_OUT_X_L_A = 0x28

disp = display.create_display()
i2c = I2C(2, freq=400000)

devices = i2c.scan()

x, y, z = 0, 0, 0

