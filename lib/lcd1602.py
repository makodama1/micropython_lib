# 必要なライブラリをインポート
from machine import Pin, I2C
from time import sleep_us

class LCD1602:
    """LCD1602 Control Class"""

    # I2CアクセスのWiat時間(基本)： 10us
    _WAIT_BASE = 10

    def __init__(self, id, sda_pin, scl_pin) -> None:
        """__init__

        ### Discription:
            __init__

        ### Args:
            id (_type_): i2c interface
            sda_pin (_type_): SDA Pin Number
            scl_pin (_type_): SCL Pin Number
        """
        # インスタンス変数初期化
        self._bit_mode = 1  # 8bit mode
        self._line = 0x80   # 2 Line
        self._font = 0x00   # 5x8 font

        # Display
        self._display_enable = 0x00

        # Cursor
        self._cursor_enable = 0x00
        self._blink_enable = 0x00
        self._cursor_pos_row = 0
        self._cursor_pos_col = 0

        # I2C を初期化
        self.i2c = I2C(id, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=100000)

        i2c_addr_list = self.i2c.scan()
        self.i2c_addr = i2c_addr_list[0]

        print("i2c_addr:{:#x}".format(self.i2c_addr))

        # LCD1602 を初期化(4bit Mode)
        self._set_4bit_mode()
        # 2行 5x8 Font に設定
        self.display_line_set()
        self.display_font_set()
        # Display Clear
        self.display_clear()

    def _set_4bit_mode(self) -> None:
        """_set_4bit_mode

        ### Discription:
            Set 4bit Mode
        """
        # wait 15ms
        sleep_us(15000)
        # Set 8bit mode initially
        self._write_4bits(0x03)
        # wait 5ms
        sleep_us(5000)
        # Set 8bit mode initially
        self._write_4bits(0x03)
        # wait 100us
        sleep_us(100)
        # Set 8bit mode initially
        self._write_4bits(0x03)
        # Set 4bit mode initially
        self._write_4bits(0x02)
        self._bit_mode = 0
        # wait 100us
        sleep_us(100)
    
    def _write_4bits(self, bits) -> None:
        """_write_4bits

        ### Discription: 
            Write 4bits
        
        ### Args:
            bits (_type_): _description_
        """

        buf = bits << 4
        # 0xC: BL=1, E=1, R/W=0, RS=0
        self.i2c.writeto(self.i2c_addr, bytes([buf | 0x0C]))
        sleep_us(self._WAIT_BASE)
        # 0xFB: 1011 -> only E=0
        self.i2c.writeto(self.i2c_addr, bytes([buf & 0xFB]))

    def _write_command(self, command) -> None:
        """_write_command

        ### Discription: 
            Write one byte command by dividing higher and lower 4bits

        ### Args:
            command (_type_): _description_
        """
        # Write higher bits
        # 0xC: BL=1, E=1, R/W=0, RS=0
        buf = command & 0xF0 | 0x0C
        self.i2c.writeto(self.i2c_addr, bytes([buf]))
        sleep_us(self._WAIT_BASE)
        # 0xFB: 1011 -> only E=0
        self.i2c.writeto(self.i2c_addr, bytes([buf & 0xFB]))
        # Write lower bits    
        # 0xC: BL=1, E=1, R/W=0, RS=0
        buf = ((command << 4) & 0xF0) | 0x0C
        self.i2c.writeto(self.i2c_addr, bytes([buf]))
        sleep_us(self._WAIT_BASE)
        # 0xFB: 1011 -> only E=0
        self.i2c.writeto(self.i2c_addr, bytes([buf & 0xFB]))
        
    def write_char(self, char) -> None:
        """write_char

        ### Discription: 
            Write Charactor
        
        ### Args:
            char (_type_): ASCII charactor
        """

        # convert unicode
        unicode = ord(char)

        # Write higher bits
        # 0xD: BL=1, E=1, R/W=0, RS=1
        buf = unicode & 0xF0 | 0x0D
        self.i2c.writeto(self.i2c_addr, bytes([buf]))
        sleep_us(self._WAIT_BASE)
        # 0xFB: 1011 -> only E=0
        self.i2c.writeto(self.i2c_addr, bytes([buf & 0xFB]))
        # Write lower bits    
        # 0xD: BL=1, E=1, R/W=0, RS=1
        buf = ((unicode << 4) & 0xF0) | 0x0D
        self.i2c.writeto(self.i2c_addr, bytes([buf]))
        sleep_us(self._WAIT_BASE)
        # 0xFB: 1011 -> only E=0
        self.i2c.writeto(self.i2c_addr, bytes([buf & 0xFB]))

    def display_clear(self) -> None:
        """display_clear

        ### Commands:
            Display Clear: 0000|0001
        """

        # command write 
        self._write_command(0x01)
        # wait 1.5ms
        sleep_us(1500)

    def cursor_pos_init(self) -> None:
        """cursor_pos_init

        ### Commands:
            Cursor Return Home: 0000|0010
        """

        self._cursor_pos_row = 0
        self._cursor_pos_col = 0

        # command write 
        self._write_command(0x02)
        # wait 1.5ms
        sleep_us(1500)
        
    def entry_mode_set(self, i_d=1, s=0) -> None:
        """entry_mode_set

        ### Command:
            Entry mode: 0000|01(I/D)S
            I/D: 0(Cursor Left move), 1(Cursor Right move)
            S: 0(Data Shift OFF), 1(Data Shift ON)

        ### Args:
            i_d (int, optional): 0(Cursor Left move), 1(Cursor Right move). Defaults to 1.
            s (int, optional): 0(Data Shift OFF), 1(Data Shift ON). Defaults to 0.
        """
        command = 0x04
        # Cursor Right Move
        if i_d == 1:
            command = command | 0x02

        # Data Shift On
        if s == 1:
            command = command | 0x01

        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def display_enable(self, enable=False) -> None:
        """display_enable

        ### Commands:
            Display ON\OFF: 0000|1DCB
            DL: 0(Display disable), 1(Display enable)
            C: 0(Cursor disable), 1(Cursor enable)
            B: 0(Blink disable), 1(Blink enable)

        ### Args:
            enable (bool, optional): DL: False(Display disable), True(Display enable). Defaults to False.
        """

        command = 0x08
        # Display On
        if enable == True:
            self._display_enable = 0x04
        else:
            self._display_enable = 0x00

        command = command | (self._display_enable | self._cursor_enable | self._blink_enable)

        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def cursor_enable(self, enable=False) -> None:
        """cursor_enable

        ### Commands:
            Display ON\OFF: 0000|1DCB
            DL: 0(Display disable), 1(Display enable)
            C: 0(Cursor disable), 1(Cursor enable)
            B: 0(Blink disable), 1(Blink enable)

        ### Args:
            enable (bool, optional): C: False(Cursor disable), True(Cursor enable). Defaults to False.
        """

        command = 0x08
        # Cursor On
        if enable == True:
            self._cursor_enable = 0x02
        else:
            self._cursor_enable = 0x00

        command = command | (self._display_enable | self._cursor_enable | self._blink_enable)

        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def blink_enable(self, enable=False) -> None:
        """blink_enable

        ### Commands:
            Display ON\OFF: 0000|1DCB
            DL: 0(Display disable), 1(Display enable)
            C: 0(Cursor disable), 1(Cursor enable)
            B: 0(Blink disable), 1(Blink enable)

        ### Args:
            enable (bool, optional): B: False(Blink disable), True(Blink enable). Defaults to False.
        """

        command = 0x08
        # Cursor On
        if enable == True:
            self._blink_enable = 0x01
        else:
            self._blink_enable = 0x00

        command = command | (self._display_enable | self._cursor_enable | self._blink_enable)

        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def cursor_move_right(self) -> None:
        """cursor_move_right

        ### Command:
            Cursor Display Shift: 0001|(S/C)(R/L)00
            S/C: 0(Cursor Move)
            R/L: 1(Right Move)
        """

        self._cursor_pos_col = self._cursor_pos_col + 1
        if self._cursor_pos_col == 16:
            self._cursor_pos_col = 0
            self._cursor_pos_row = self._cursor_pos_row + 1
            if self._cursor_pos_row == 2:
                self._cursor_pos_row = 0

        print("cursor pos col:{:#d} cursor pos row:{:#d} ".format(self._cursor_pos_col, self._cursor_pos_row))

        command = 0x14
        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def cursor_move_left(self) -> None:
        """cursor_move_left

        ### Command:
            Cursor Display Shift: 0001|(S/C)(R/L)00
            S/C: 0(Cursor Move)
            R/L: 0(Left Move)
        """

        self._cursor_pos_col = self._cursor_pos_col - 1
        if self._cursor_pos_col < 0:
            self._cursor_pos_col = 15
            self._cursor_pos_row = self._cursor_pos_row - 1
            if self._cursor_pos_row < 0:
                self._cursor_pos_row = 1

        print("cursor pos col:{:#d} cursor pos row:{:#d} ".format(self._cursor_pos_col, self._cursor_pos_row))

        command = 0x10
        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def data_shift_right(self) -> None:
        """data_shift_right

        ### Command:
            Cursor Display Shift: 0001|(S/C)(R/L)00
            S/C: 1(Display Shift)
            R/L: 1(Right Move)
        """

        command = 0x1C
        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def data_shift_left(self) -> None:
        """cursor_move_right

        ### Command:
            Cursor Display Shift: 0001|(S/C)(R/L)00
            S/C: 1(Display Shift)
            R/L: 0(Left Move)
        """

        command = 0x18
        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def display_line_set(self, num = 2) -> None:
        """display_line_set

        ### Command:
            Function set: 001(DL)|NFxx
            DL: 0(4bit mode), 1(8bit mode)
            N: 0(1 line), 1(2 lines)
            F: 0(5x8 font), 1(5x11 font)

        ### Args:
            num (int, optional): 1(1 line), 2(2 lines). Defaults to 2.
        """

        command = 0x20
        if num == 1:
            self._line = 0x00
        elif num == 2:
            self._line = 0x08
        else:
            return
        
        command = command  | (self._bit_mode | self._line | self._font)
        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def display_font_set(self, font = 0) -> None:
        """display_line_set

        ### Command:
            Function set: 001(DL)|NFxx
            DL: 0(4bit mode), 1(8bit mode)
            N: 0(1 line), 1(2 lines)
            F: 0(5x8 font), 1(5x11 font)

        ### Args:
            font (int, optional): 0(5x8 font), 1(5x11 font). Defaults to 0.
        """

        command = 0x20
        if font == 0:
            self._font = 0x00
        elif font == 1:
            self._font = 0x04
        else:
            return
        
        command = command  | (self._bit_mode | self._line | self._font)
        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    # Commands
    # Curosor Pos Set:
    # row=1～2
    # col=1～16
    def cursor_pos_set(self, row=1, col=1) -> None:
        command = 0x80

        if 1 <= col <= 16:
            pass
        else:
            return
        
        if 1 <= row <= 2:
            pass
        else:
            return

        self._cursor_pos_col = (col-1)
        self._cursor_pos_row = (row-1)

        pos = (self._cursor_pos_col) + (0x40 * (self._cursor_pos_row))
        command = command | pos

        # command write 
        self._write_command(command)
        # wait 40us
        sleep_us(40)

    def print_line(self, line, str) -> None:
        """print_line

        ### Discription: 
            Write Line

        ### Args:
            line (_type_): display line
            str (_type_): display string
        """        

        if((line != 1) and (line != 2)):
            print("line is invalid.")
            return

        if(len(str) > 16):
            print("str length over size.")
            return
        
        self.cursor_pos_set(line, 1)

        for index in range(len(str)):
            self.write_char(str[index])
