import datetime
import RPi.GPIO as GPIO
import schedule
import time

GPIO.setmode(GPIO.BCM)
LedPin = 18
buttonPin = 12

GPIO.setwarnings(False)
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LedPin, GPIO.OUT)
GPIO.output(LedPin, GPIO.LOW)

pulse = True
pwm = GPIO.PWM(LedPin, 500)

def button_pressed(channel):
    global pulse
    global pwm
    pulse = False
    pwm.stop()
    GPIO.output(LedPin, GPIO.LOW) # Turn off LED
    time_now = datetime.datetime.now()
    formatted_time = time_now.strftime("%m-%d-%Y %I:%M %p\n")
    print("LED stopped by button at", formatted_time)

def fade_led():
    global pulse
    global pwm
    pulse = True
    time_now = datetime.datetime.now()
    formatted_time = time_now.strftime("%m-%d-%Y %I:%M %p\n")
    print("LED pulsing started at", formatted_time)
    while pulse:
        pwm.start(0) 
        for dc in range(0, 101, 5):   # Increase duty cycle: 0~100
            pwm.ChangeDutyCycle(dc)     # Change duty cycle
            time.sleep(0.05)
        time.sleep(1)
        for dc in range(100, -1, -5): # Decrease duty cycle: 100~0
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.05)
        time.sleep(1)

# Add an event detection for the button
GPIO.add_event_detect(buttonPin, GPIO.RISING, callback=button_pressed, bouncetime=300)
        
schedule.every().day.at("06:00").do(fade_led)
#schedule.every(2).days.at("20:30").do(fade_led)
schedule.every().day.at("20:30").do(fade_led)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    pwm.stop()
    GPIO.output(LedPin, GPIO.LOW)    
    GPIO.cleanup()
    print("stopped")
