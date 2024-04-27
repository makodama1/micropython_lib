from lib import LCD1602

IF_NO = 1
SDA_PIN_NO = 18
SDC_PIN_NO = 19

if __name__ == "__main__":
    # LCD1602 インスタンス生成(Interface=１, SDA=Pin(18), SCL=Pin(19))
    lcd1602 = LCD1602(IF_NO, SDA_PIN_NO, SDC_PIN_NO)

    ## LCD1602 初期化
    # Display Off
    lcd1602.display_enable(False)
    # Display Clear
    lcd1602.display_clear()
    # Cursor Right move, Data Shit OFF
    lcd1602.entry_mode_set(1,0)
    # Display ON, Corsor OFF, Blink Off
    lcd1602.display_enable(True)
    # Display Clear
    lcd1602.display_clear()

    # Display Set "Hello" to Line 1
    lcd1602.print_line(1, "Hello")
    # Display Set "World" to Line 1
    lcd1602.print_line(2, "World")


