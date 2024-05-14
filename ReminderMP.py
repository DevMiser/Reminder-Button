# the following program is provided by DevMiser - https://github.com/DevMiser
# this program is in MicroPython for running on a Raspberry Pi Pico W

import machine
import network # handles connecting to WiFi
import time
import ntptime # handles connecting to network time protocol (NTP)

# Fill in your WiFi network name (ssid) and password here:
ssid = ''
password = ''

# Function to connect to WiFi
def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')

# Initialize LED pin
LedPin = 6
led = machine.PWM(machine.Pin(LedPin))
led.freq(500)  # Set PWM frequency to 500 Hz
led.duty_u16(0)  # Turn off LED initially

# Initialize button pin
buttonPin = 10
button = machine.Pin(buttonPin, machine.Pin.IN, machine.Pin.PULL_UP)

# Global variable to control LED pulsing
pulse = True

# Function to stop LED pulsing upon button push

def button_pressed(pin):
    global pulse
    if pulse:
        time_now = time.localtime(time.mktime(time.localtime()) - 4 * 60 * 60)
        formatted_time = "{:02d}-{:02d}-{:04d} {:02d}:{:02d} {}".format(
        time_now[1], time_now[2], time_now[0],
        (time_now[3] % 12) or 12,  # Convert to 12-hour format
        time_now[4],
        "AM" if time_now[3] < 12 else "PM"
        )
        print("LED stopped by button at", formatted_time)
    pulse = False

# Function to pulse LED
def fade_led():
    global pulse
    if pulse:
        time_now = time.localtime(time.mktime(time.localtime()) - 4 * 60 * 60)
        formatted_time = "{:02d}-{:02d}-{:04d} {:02d}:{:02d} {}".format(
        time_now[1], time_now[2], time_now[0],
        (time_now[3] % 12) or 12,  # Convert to 12-hour format
        time_now[4],
        "AM" if time_now[3] < 12 else "PM"
        )
        print("LED pulsing started at", formatted_time)
    while pulse:
        for dc in range(0, 65536, 3277):  # Increase duty cycle: 0~65535
            led.duty_u16(dc)
            time.sleep_ms(50)
        time.sleep(1)
        for dc in range(65535, -1, -3277):  # Decrease duty cycle: 65535~0
            led.duty_u16(dc)
            time.sleep_ms(50)
        led.duty_u16(0)
        time.sleep(1)

# Button interrupt
button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_pressed)

# Connect to WiFi
connect()

# Synchronize time with NTP server
ntptime.settime()

# Schedule LED pulsing based on time
while True:

    current_time = time.localtime(time.mktime(time.localtime()) - 4 * 60 * 60) # adjusts 4 hours from UTC
    if current_time[3] == 6 and current_time[4] == 30: #6:30 AM - hours [3] are in 24 hour format
        pulse = True
        fade_led() 
        time.sleep(60)
    elif current_time[3] == 20 and current_time[4] == 30: #8:30 PM - hours [3] are in 24 hour format
        pulse = True
        fade_led()
        time.sleep(60)
    time.sleep(1)
