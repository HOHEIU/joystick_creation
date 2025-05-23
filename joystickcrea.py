import machine
import time
import random

# 設定 LED 腳位（實際接腳請自行調整）
led_pins = [16, 17, 18, 19, 23, 5, 2, 22]
leds = [machine.Pin(pin, machine.Pin.OUT) for pin in led_pins]

# 設定 Joystick ADC（VRX 接 GPIO34）
adc = machine.ADC(machine.Pin(34))
adc.atten(machine.ADC.ATTN_11DB)
adc.width(machine.ADC.WIDTH_10BIT)

# 防抖與控制
def debounce_delay():
    time.sleep(0.25)

def light_led(index):
    for i, led in enumerate(leds):
        led.value(1 if i == index else 0)
        
def check_joystick_connected():
    test_value = adc.read()
    print("🎮 Joystick ADC 測試值:", test_value)
    # 若讀值接近 0 或接近最大值，可能是沒接上（浮空）
    return 50 < test_value < 1000

def move_bomb(current_index):
    adc_val = adc.read()
    if adc_val < 400 and current_index > 0:
        return current_index - 1
    elif adc_val > 600 and current_index < len(leds) - 1:
        return current_index + 1
    return current_index

def bomb_defuse_game():
    if not check_joystick_connected():
        print("⚠️ Joystick 未連接，請檢查 VRX → GPIO34")
        return

    print("💣 遊戲開始：解除炸彈！用 Joystick 把 LED 推到最右邊")

    while True:
        bomb_index = random.randint(0, len(leds) - 2)
        current_index = bomb_index
        time_limit = 10
        start_time = time.time()
        last_shown_second = -1  # 避免每迴圈都 print

        light_led(current_index)

        while True:
            now = time.time()
            elapsed = int(now - start_time)
            remaining = time_limit - elapsed

            # ⏱️ 每秒只顯示一次倒數（避免刷太快）
            if remaining != last_shown_second and remaining >= 0:
                print(f"⏱️ 倒數：{remaining} 秒")
                last_shown_second = remaining

            # 移動炸彈
            new_index = move_bomb(current_index)
            if new_index != current_index:
                current_index = new_index
                light_led(current_index)
                print(f"➡️ 移動至 LED index: {current_index}")
                debounce_delay()

            if current_index == len(leds) - 1:
                print("✅ 成功解除炸彈！")
                break
            if elapsed >= time_limit:
                print("💥 時間到！炸彈爆炸了！")
                for _ in range(6):
                    for led in leds:
                        led.value(1)
                    time.sleep(0.2)
                    for led in leds:
                        led.value(0)
                    time.sleep(0.2)
                return

        time.sleep(2)
        print("\n下一回合開始...\n")

# 啟動遊戲
bomb_defuse_game()
