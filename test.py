import pigpio
import time
pi = pigpio.pi()

# drive_forward_pin = 26
# drive_backward_pin = 20
# steering_pin = 5

# # Motor driver PWM
# print('Test motor')
# pi.set_PWM_frequency(drive_forward_pin, 8000)
# pi.set_PWM_frequency(drive_backward_pin, 8000)

# pi.set_PWM_dutycycle(drive_forward_pin, 0)
# pi.set_PWM_dutycycle(drive_backward_pin, 30)
# # Steering servo PWM

# pi.set_servo_pulsewidth(steering_pin, 1650)

# pi.set_mode(6, pigpio.OUTPUT)
# pi.write(6,0)
# # pi.set_PWM_frequency(6, 8000)
# # pi.set_PWM_dutycycle(6, 30)

# while True:
#     pass

############################################################################################################


# count = 0
# def HE_callback(gpio, level, tick):
#     global count
#     print("Count:", count)
#     count += 1

# he_pin = 17
# print('test')
# # Hall effect sensor
# pi.set_glitch_filter(he_pin, 100)
# pi.callback(he_pin, pigpio.RISING_EDGE, HE_callback)

# while True:
#     pass


##############################################################################################################


# # Ultrasonic sensor
# pi.set_pull_up_down(2, pigpio.PUD_UP)
# pi.set_pull_up_down(3, pigpio.PUD_UP)
# us_handle = pi.i2c_open(1, 0x57)

# while True:
#     time.sleep(1)
#     pi.i2c_write_byte(us_handle, 1)
#     time.sleep(30/1000)
#     (count, data) = pi.i2c_read_device(us_handle, 3)
#     if not count == 3:
#         print("Error in reading ultrasonic sensor")
#         break
#     distance = int.from_bytes(data, 'big')/1000000 # Distance in meters
#     print("Distance:", distance)

#########################################################################################################

# import RPi.GPIO as GPIO                # import GPIO
# from hx711 import HX711                # import the class HX711

# GPIO.setmode(GPIO.BCM)                 # set GPIO pin mode to BCM numbering
# hx = HX711(dout_pin=22, pd_sck_pin=27)

# while True:
#     reading = hx.get_raw_data_mean(readings=5)
#     print(reading)


#set GPIO Pins
# trigger_pin = 25
# echo_pin = 8
 

 
# def distance():
#     # set Trigger to HIGH
#     pi.write(trigger_pin, 1)
 
#     # set Trigger after 0.01ms to LOW
#     time.sleep(0.00001)
#     pi.write(trigger_pin, 0)
 
#     StartTime = time.time()
#     StopTime = time.time()
 
#     # save StartTime
#     while pi.read(echo_pin) == 0:
#         StartTime = time.time()
 
#     # save time of arrival
#     while pi.read(echo_pin) == 1:
#         StopTime = time.time()
 
#     # time difference between start and arrival
#     TimeElapsed = StopTime - StartTime
#     # multiply with the sonic speed (34300 cm/s)
#     # and divide by 2, because there and back
#     distance = (TimeElapsed * 343) / 2
 
#     return distance

# while True:
#     print(distance())
#     time.sleep(0.5)

# # Ultrasonic sensor reading thread

# from threading import Thread
# ultrasonicDist = 0
# us_trig_pin = 25
# us_echo_pin = 8

# # def ultrasonicReader():
# # global ultrasonicDist
# # global us_trig_pin
# # global us_echo_pin

# def distance():
#     # set Trigger to HIGH
#     pi.write(trigger_pin, 1)

#     # set Trigger after 0.01ms to LOW
#     time.sleep(0.00001)
#     pi.write(trigger_pin, 0)

#     StartTime = time.time()
#     StopTime = time.time()

#     # save StartTime
#     while pi.read(echo_pin) == 0:
#         StartTime = time.time()

#     # save time of arrival
#     while pi.read(echo_pin) == 1:
#         StopTime = time.time()

#     # time difference between start and arrival
#     TimeElapsed = StopTime - StartTime
#     # multiply with the sonic speed (34300 cm/s)
#     # and divide by 2, because there and back
#     distance = (TimeElapsed * 3430000) / 2

#     return distance

# while True:
#     ultrasonicDist = distance()
#     print(ultrasonicDist)
#     time.sleep(0.5)

# # Start ultrasonic sensor thread
# ultrasonic_thread = Thread(target=ultrasonicReader)
# ultrasonic_thread.daemon = True
# ultrasonic_thread.start()

# while True:
#     print('Ultrasonic:', ultrasonicDist)
#     time.sleep(1)

import RPi.GPIO as GPIO
from hcsr04sensor import sensor

GPIO.setmode(GPIO.BCM)

x = sensor.Measurement
trig = 25
echo = 8
while True:
    print(x.basic_distance(trig, echo))
    time.sleep(1)