# the following program is provided by DevMiser - https://github.com/DevMiser
# this program is in MicroPython for running on a Raspberry Pi Pico W

import machine
import network # handles connecting to WiFi 
import utime
import ntptime  # handles connecting to network time protocol (NTP)

# Set your network name (SSID) and password here:
ssid = ''
password = ''

# Function to connect to WiFi
def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('Waiting for connection...')
        utime.sleep(1)
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

# Function to stop pulsing LED
def button_pressed(pin):
    global pulse
    if pulse:
        time_now = utime.localtime()
        formatted_time = "{:02d}-{:02d}-{:04d} {:02d}:{:02d} {}".format(
            time_now[1], time_now[2], time_now[0], time_now[3], time_now[4],
            "AM" if time_now[3] < 12 else "PM"
        )
        print("LED stopped by button at", formatted_time)
    pulse = False
    # Immediately turn off the LED when the button is pressed
    led.duty_u16(0) 

# Function to pulse LED
def fade_led():
    global pulse
    while pulse: # Keep pulsing as long as 'pulse' is True
        for dc in range(0, 65536, 3277):  # Increase duty cycle: 0~65535
            if not pulse: # Check if button was pressed during fade-in
                break
            led.duty_u16(dc)
            utime.sleep_ms(50)
        
        if not pulse: # Check after fade-in loop
            break
            
        utime.sleep(1) # Pause at full brightness
        
        for dc in range(65535, -1, -3277):  # Decrease duty cycle: 65535~0
            if not pulse: # Check if button was pressed during fade-out
                break
            led.duty_u16(dc)
            utime.sleep_ms(50)
        
        if not pulse: # Check after fade-out loop
            break
            
        led.duty_u16(0) # Ensure LED is off after a full pulse cycle
        utime.sleep(1) # Pause when off

# Button interrupt
button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_pressed)

# Connect to WiFi
connect()

# Synchronize time with NTP server
ntptime.settime()

# Schedule LED pulsing based on time
try:
    while True:
        current_time = utime.localtime(utime.mktime(utime.localtime()) - 4 * 60 * 60) # adjusts 4 hours from UTC for NYC time
        # Adjust these times as needed for your desired schedule.
        if current_time[3] == 6 and current_time[4] == 30:  # 6:30 AM
            pulse = True
            fade_led()
            led.duty_u16(0)
            utime.sleep(60) # Sleep to avoid re-entering the fade_led for the same minute

# Use the follwoing if you want to use more than one time per day:
        elif current_time[3] == 20 and current_time[4] == 00:  # 8:00 PM
            pulse = True
            fade_led()
            led.duty_u16(0)
            utime.sleep(60) # Sleep to avoid re-entering the fade_led for the same minute
        utime.sleep(1)
        
except KeyboardInterrupt:
    led.duty_u16(0) # Ensure LED is off on manual program termination
    machine.reset()
