import struct


class LSM303(object):
    ADDRESS_ACCEL = (0x32 >> 1)  # 0011001x
    ADDRESS_MAG   = (0x3C >> 1)  # 0011110x
    REGISTER_ACCEL_CTRL_REG1_A = 0x20 # 00000111   rw
    REGISTER_ACCEL_CTRL_REG4_A = 0x23 # 00000000   rw
    REGISTER_ACCEL_OUT_X_L_A   = 0x28
    REGISTER_MAG_CRB_REG_M     = 0x01
    REGISTER_MAG_MR_REG_M      = 0x02
    REGISTER_MAG_OUT_X_H_M     = 0x03

    MAGGAIN_1_3 = 0x20 # +/- 1.3
    MAGGAIN_1_9 = 0x40 # +/- 1.9
    MAGGAIN_2_5 = 0x60 # +/- 2.5
    MAGGAIN_4_0 = 0x80 # +/- 4.0
    MAGGAIN_4_7 = 0xA0 # +/- 4.7
    MAGGAIN_5_6 = 0xC0 # +/- 5.6
    MAGGAIN_8_1 = 0xE0 # +/- 8.1

    def __init__(self, i2c, hires=True):
        self.i2c = i2c
        self._data = bytearray(6)
        i2c.writeto_mem(self.ADDRESS_ACCEL, self.REGISTER_ACCEL_CTRL_REG1_A, bytearray([0x27]))

        if hires:
            i2c.writeto_mem(self.ADDRESS_ACCEL, self.REGISTER_ACCEL_CTRL_REG4_A, bytearray([0b00001000]))
        else:
            i2c.writeto_mem(self.ADDRESS_ACCEL, self.REGISTER_ACCEL_CTRL_REG4_A, bytearray([0x00]))

        i2c.writeto_mem(self.ADDRESS_MAG, self.REGISTER_MAG_MR_REG_M, bytearray([0x00]))

    def read(self):
        """Read the accelerometer and magnetometer value.  A tuple of tuples will
        be returned with:
          ((accel X, accel Y, accel Z), (mag X, mag Z, mag Y))
        """
        # Read the accelerometer as signed 16-bit little endian values.
        self.i2c.readfrom_mem_into(self.ADDRESS_ACCEL, self.REGISTER_ACCEL_OUT_X_L_A | 0x80, self._data)
        accel = struct.unpack('<hhh', self._data)
        # Convert to 12-bit values by shifting unused bits.
        accel = (accel[0] >> 4, accel[1] >> 4, accel[2] >> 4)

        self.i2c.readfrom_mem_into(self.ADDRESS_MAG, self.REGISTER_MAG_OUT_X_H_M, self._data)
        mag = struct.unpack('>hhh', self._data)

        return (accel, mag)

    def set_mag_gain(self, gain=0x20):
        """Set the magnetometer gain.  Gain should be one of the following
        constants:
         - LSM303_MAGGAIN_1_3 = +/- 1.3 (default)
         - LSM303_MAGGAIN_1_9 = +/- 1.9
         - LSM303_MAGGAIN_2_5 = +/- 2.5
         - LSM303_MAGGAIN_4_0 = +/- 4.0
         - LSM303_MAGGAIN_4_7 = +/- 4.7
         - LSM303_MAGGAIN_5_6 = +/- 5.6
         - LSM303_MAGGAIN_8_1 = +/- 8.1
        """
        self.i2c.writeto_mem(self.ADDRESS_MAG, self.REGISTER_MAG_CRB_REG_M, gain)

