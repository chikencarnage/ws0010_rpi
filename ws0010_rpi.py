#!/usr/bin/python

#
# based on code from lrvick and LiquidCrystal
# lrvic - https://github.com/lrvick/raspi-hd44780/blob/master/hd44780.py
# LiquidCrystal - https://github.com/arduino/Arduino/blob/master/libraries/LiquidCrystal/LiquidCrystal.cpp
#
#
import RPi.GPIO as GPIO
from time import sleep

class Winstar_OLED(object):
    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80
 
    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00
 
    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00
 
    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
 
    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00
 
    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10s = 0x04
    LCD_5x8DOTS = 0x00


    def __init__(self, pin_rs=17, pin_rw=27, pin_e=22, pins_db=[05, 12, 13, 26]):
        # Emulate the old behavior of using RPi.GPIO if we haven't been given
        # an explicit GPIO interface to use
        self.pin_rs = pin_rs
        self.pin_rw = pin_rw
        self.pin_e = pin_e
        self.pins_db = pins_db
        self.busy_pin = pins_db[3]

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_e, GPIO.OUT)
        GPIO.setup(self.pin_rw, GPIO.OUT)
        GPIO.setup(self.pin_rs, GPIO.OUT)
        for pin in self.pins_db:
            GPIO.setup(pin, GPIO.OUT)
        GPIO.output(self.pin_e, False)
        GPIO.output(self.pin_rw, False)
        GPIO.output(self.pin_rs, False)

        self.displayfunction = self.LCD_FUNCTIONSET | self.LCD_4BITMODE
        self.displaycontrol  = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.displaymode     = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT

        self.begin(16,2)

    def begin(self, cols, lines):
        self.numlines = lines
        self.currline = 0

        GPIO.setup(self.pin_e, GPIO.OUT)
        GPIO.setup(self.pin_rw, GPIO.OUT)
        GPIO.setup(self.pin_rs, GPIO.OUT)

        GPIO.output(self.pin_e, False)
        GPIO.output(self.pin_rw, False)
        GPIO.output(self.pin_rs, False)

        self.delayMicroseconds(50000)

        for pin in self.pins_db:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

        self.write4bits(0x03)
        self.delayMicroseconds(5000)
        self.write4bits(0x08)
        self.delayMicroseconds(5000)

        self.write4bits(0x03)  # added
        self.delayMicroseconds(5000)
        self.write4bits(0x03)  # added
        self.delayMicroseconds(5000)
        self.write4bits(0x02)  # initialization
        self.delayMicroseconds(5000)
        self.write4bits(0x02)  # initialization
        #self.delayMicroseconds(5000)
        self.write4bits(0x0C)  # 2 line 5x8 matrix originally 08
        self.delayMicroseconds(5000) # added
        self.write4bits(0x0)  # initialization # added
        #self.delayMicroseconds(5000)
        self.write4bits(0x0C)  # 2 line 5x8 matrix originally 08 added
        self.delayMicroseconds(5000) # added
        
        self.write4bits(0x0) # originally 0x08
        #self.delayMicroseconds(5000)
        self.write4bits(0x01)
        self.delayMicroseconds(5000)
        self.write4bits(0x0) # added
        #self.delayMicroseconds(5000)
        self.write4bits(0x06)
        self.delayMicroseconds(5000)
        self.write4bits(0x0) # 0x02
        #self.delayMicroseconds(5000)
        self.write4bits(0x00) # 0x00
        self.delayMicroseconds(10000) # 5000

    def home(self):
        self.write4bits(self.LCD_RETURNHOME)  # set cursor position to zero
        # self.delayMicroseconds(3000)  # this command takes a long time!

    def clear(self):
        self.write4bits(self.LCD_CLEARDISPLAY)  # command to clear display
        # self.delayMicroseconds(3000)  # 3000 microsecond sleep, clearing the display takes a long time

    def setCursor(self, col, row):
        self.row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row >= self.numlines:
            row = row % (self.numlines - 1)  # we count rows starting w/0
        self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def noDisplay(self):
        """ Turn the display off (quickly) """
        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def display(self):
        """ Turn the display on (quickly) """
        self.displaycontrol |= self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noCursor(self):
        """ Turns the underline cursor off """
        self.displaycontrol &= ~self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def cursor(self):
        """ Turns the underline cursor on """
        self.displaycontrol |= self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noBlink(self):
        """ Turn the blinking cursor off """
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def blink(self):
        """ Turn the blinking cursor on """
        self.displaycontrol |= self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def DisplayLeft(self):
        """ These commands scroll the display without changing the RAM """
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)

    def scrollDisplayRight(self):
        """ These commands scroll the display without changing the RAM """
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT)

    def leftToRight(self):
        """ This is for text that flows Left to Right """
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def rightToLeft(self):
        """ This is for text that flows Right to Left """
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def autoscroll(self):
        """ This will 'right justify' text from the cursor """
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def noAutoscroll(self):
        """ This will 'left justify' text from the cursor """
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def write4bits(self, bits, char_mode=False):
        """ Send command to LCD """
        self.delayMicroseconds(1000)  # 1000 microsecond sleep
        bits = bin(bits)[2:].zfill(8)
        GPIO.output(self.pin_rs, char_mode)
        for pin in self.pins_db:
            GPIO.output(pin, False)
        for i in range(4):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i], True)
        self.pulseEnable()
        for pin in self.pins_db:
            GPIO.output(pin, False)
        for i in range(4, 8):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i-4], True)
        self.pulseEnable()
        self.waitForReady()

    def delayMicroseconds(self, microseconds):
        seconds = microseconds / float(1000000)  # divide microseconds by 1 million for seconds
        sleep(seconds)

    def pulseEnable(self):
        GPIO.output(self.pin_e, True)
        self.delayMicroseconds(50)       # 1 microsecond pause - enable pulse must be > 450ns
        GPIO.output(self.pin_e, False)

    def waitForReady(self):
        busy = True
        GPIO.setup(self.busy_pin, GPIO.IN)
        GPIO.output(self.pin_rs, False)
        GPIO.output(self.pin_rw, True)
        while busy == True:
            GPIO.output(self.pin_e, False)
            GPIO.output(self.pin_e, True)
            self.delayMicroseconds(10)
            busy = GPIO.input(self.busy_pin)
            GPIO.output(self.pin_e, False)
            self.pulseEnable()
        GPIO.setup(self.busy_pin, GPIO.OUT)
        GPIO.output(self.pin_rw, False)

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""
        for char in text:
            if char == '\n':
                self.write4bits(0xC0)  # next line
            else:
                self.write4bits(ord(char), True)


if __name__ == '__main__':
    lcd = Adafruit_CharLCD()
    lcd.clear()
    lcd.message("  Adafruit 16x2\n  Standard LCD")
