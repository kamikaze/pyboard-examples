import pyb
from lcd160cr import LCD160CR, PORTRAIT_UPSIDEDOWN


def run_igniter_test(base_pin_name='Y12'):
    pin = pyb.Pin(base_pin_name, pyb.Pin.OUT_PP)
    pin.low()
    lcd = LCD160CR('X')
    lcd.set_orient(PORTRAIT_UPSIDEDOWN)
    lcd.set_text_color(lcd.rgb(255, 0, 0), lcd.rgb(0, 0, 0))
    lcd.set_font(3)
    lcd.erase()

    countdown = 15000
    remaining = countdown
    start = pyb.millis()

    while True:
        remaining = countdown - pyb.elapsed_millis(start)
        if remaining <= 0:
            break

        lcd.erase()
        lcd.set_pos(40, 80)

        lcd.write('{:.2f}'.format(remaining / 1000))

        pyb.delay(51)

    lcd.erase()
    pin.high()
    lcd.set_pos(40, 80)
    lcd.write('BOOM !!!')
    pin.low()

