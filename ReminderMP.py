# the following program is provided by DevMiser - https://github.com/DevMiser
# this program is in MicroPython for running on a Raspberry Pi Pico W

import machine
import network   # handles connecting to WiFi
import urequests # handles making and servicing network requests
import utime

utime.sleep(10)

# Fill in your WiFi network name (ssid) and password here:
ssid = ''
password = ''

# Function to connect to WiFi
def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        utime.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')

# Set pin numbers for LED and button
LedPin = 6
buttonPin = 10

# Initialize LED pin
led = machine.PWM(machine.Pin(LedPin))
led.freq(500)  # Set PWM frequency to 500 Hz
led.duty_u16(0)  # Turn off LED initially

# Initialize button pin
button = machine.Pin(buttonPin, machine.Pin.IN, machine.Pin.PULL_UP)

# Global variable to control LED pulsing
pulse = True

def button_pressed(pin):
    global pulse
    if pulse:
        time_now = utime.localtime()
        formatted_time = "{:02d}-{:02d}-{:04d} {:02d}:{:02d} {}".format(
            time_now[1], time_now[2], time_now[0], time_now[3], time_now[4],
            "AM" if time_now[3] < 12 else "PM"
        )
        print("LED stopped by button at", formatted_time)        
    else:
        pass
    pulse = False

def fade_led():
    global pulse
    time_now = utime.localtime()
    formatted_time = "{:02d}-{:02d}-{:04d} {:02d}:{:02d} {}".format(
        time_now[1], time_now[2], time_now[0], time_now[3], time_now[4],
        "AM" if time_now[3] < 12 else "PM"
    )
    if pulse:
        print("LED pulsing started at", formatted_time)
    else:
        pass
    while pulse:
        for dc in range(0, 65536, 3277):  # Increase duty cycle: 0~65535
            led.duty_u16(dc)
            utime.sleep_ms(50)
        utime.sleep(1)
        for dc in range(65535, -1, -3277):  # Decrease duty cycle: 65535~0
            led.duty_u16(dc)
            utime.sleep_ms(50)
        led.duty_u16(0)
        utime.sleep(1)

# Attach button interrupt
button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_pressed)

# Schedule LED pulsing
try:
    connect()
    while True:
        fade_led()
        current_time = utime.localtime()
        if current_time[3] == 12 and current_time[4] == 54: # 6:30AM
            pulse = True
            fade_led()
            utime.sleep(60)
        elif current_time[3] == 12 and current_time[4] == 55: # 8:30PM
            pulse = True
            fade_led()
            utime.sleep(60)
        utime.sleep(1)
    
except KeyboardInterrupt:
    machine.reset()    
