import dht
import time
from machine import Pin
from lib import LCD1602

# DHT11
DHT11_PIN_NO = 16

# LCD1602
LCD1602_IF_NO = 1
LCD1602_SDA_PIN_NO = 18
LCD1602_SCL_PIN_NO = 19

if __name__ == "__main__":
    # LCD1602 インスタンス生成(Interface=１, SDA=Pin(18), SCL=Pin(19))
    lcd1602 = LCD1602(LCD1602_IF_NO, LCD1602_SDA_PIN_NO, LCD1602_SCL_PIN_NO)

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

    # Display Set "Temperature:" to Line 1
    lcd1602.print_line(1,"Temp    :")
    # Display Set "Humidity   :" to Line 1
    lcd1602.print_line(2,"Humidity:")

    dht_sensor = dht.DHT11(Pin(DHT11_PIN_NO))

    while True:
        try:
            # 測定を行う
            dht_sensor.measure()
            
            # 温度と湿度を取得
            temperature_celsius = dht_sensor.temperature()
            humidity_percentage = dht_sensor.humidity()
            
            # 結果文字列更新
            lcd1602.print_pos(1, 11, "{:.1f}C".format(temperature_celsius))
            lcd1602.print_pos(2, 11, "{:.1f}%".format(humidity_percentage))

            # 1秒待機
            time.sleep(1)
            
        except Exception as e:
            print("エラー:", e)



