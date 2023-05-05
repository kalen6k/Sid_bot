#!/usr/bin/env python3

import RPi.GPIO as GPIO
import pigpio
import time
import serial
from threading import Thread
import atexit
from hx711 import HX711
import board
import adafruit_bno055
from hcsr04sensor import sensor

# Robot states
IDLE = 0
GETTING_MESSAGE = 1
DELIVERING = 2
FETCHING_1 = 3
FETCHING_2 = 4


# For car orientation and driving direction
FORWARD = 0
BACKWARD = 1
# Turning inputs
LEFT = 2
RIGHT = 3
# Driving axis
HORIZONTAL = 4
VERTICAL = 5

## These need to be tuned
KP_STEER_ANGLE = 20
KI_STEER_ANGLE = 1
KP_STEER_POS = 5

CONSTANT_MOTOR = 50

STRAIGHT_STEERING = 1285
LEFT_STEERING = 920
RIGHT_STEERING = 1650
MIN_STRAIGHT_ADJUST = 920
MAX_STRAIGHT_ADJUST = 1650

HE_TICKS_IN_TURN = 26 # Number of Hall effect ticks in a 90 degree turn

# Additional space needed for turns
TURN_MARGIN = 3 # 1.5 in reality

SCALE_THRESHOLD = 772000 # Needs to be adjusted
OBSTACLE_THRESHOLD = 50

# Coordinates in feet
benchX = {}
benchX.update(dict.fromkeys(["201","202","203","204","205","206"], -19.0))
benchX.update(dict.fromkeys(["207","208","209","210","211","212"], -7.25))
benchX.update(dict.fromkeys(["301","302","303","304","305","306"], 4.25))
benchX.update(dict.fromkeys(["307","308","309","310","311","312"], 15.75))
benchX.update(dict.fromkeys(["401","402","403","404","405","406"], 27.75))
benchX.update(dict.fromkeys(["407","408","409","410","411","412"], 39.0))

benchY = {}
benchY.update(dict.fromkeys(["201","206","207","212","301","306","307","312","401","406","407","412"], 30.0))
benchY.update(dict.fromkeys(["202","205","208","211","302","305","308","311","402","405","408","411"], 38.0))
benchY.update(dict.fromkeys(["203","204","209","210","303","304","309","310","403","404","409","410"], 46.0))

# Global variables
posX = 0
posY = 0
past_time = 0
speed = 0
orientation = FORWARD
ultrasonicDist = 0
weight = 0
he_count = 0
pi = pigpio.pi()
ser = serial.Serial(port="/dev/ttyS0", baudrate=115200) # Use "dmesg" to figure out USB port
GPIO.setmode(GPIO.BCM)

# Thread that constantly reads the latest position from the Decawave board
def receive_position():
    global posX
    global posY

    # Setup Decawave board
    ser.write("\r\r".encode())    # Enter UART Shell mode
    time.sleep(1)
    ser.write("lep\r".encode())   # Start receiving position
    time.sleep(1)

    buffer_string = ''
    while True:
        buffer_string = buffer_string + ser.read(ser.inWaiting()).decode()
        if '\n' in buffer_string:
            lines = buffer_string.split('\n') # Guaranteed to have at least 2 entries
            if lines[-2]:
                data = lines[-2]
                data = data.replace("\r\n", "")
                data = data.split(",")
                if("POS" in data):
                    posX = float(data[data.index("POS")+1]) * 3.281
                    posY = float(data[data.index("POS")+2]) * 3.281
                    
            buffer_string = lines[-1]

# Ultrasonic sensor reading thread
def ultrasonicReader():
    global ultrasonicDist

    s = sensor.Measurement
    while True:
        ultrasonicDist = s.basic_distance(us_trig_pin, us_echo_pin)
        time.sleep(60/1000)

def scaleReader():
    hx = HX711(dout_pin=22, pd_sck_pin=27)
    global weight

    while True:
        weight = hx.get_raw_data_mean(readings=5)

# Hall effect sensor interrupt
def HE_callback(gpio, level, tick):
        global speed
        global past_time
        global he_count
        
        he_count += 1
        current_time = time.perf_counter()
        speed = (40/302) / (current_time - past_time) # Velocity in ft/sec
        past_time = current_time
        



# Turn function for testing navigation
# def turn(turnDir, driveDir):
#     if turnDir == LEFT:
#         if driveDir == FORWARD:
#             print('Turn left forward')
#         if driveDir == BACKWARD:
#             print('Turn left backward')
#     if turnDir == RIGHT:
#         if driveDir == FORWARD:
#             print('Turn right forward')
#         if driveDir == BACKWARD:
#             print('Turn right backward')

def turn(turnDir, driveDir):
    if turnDir == LEFT:
        if driveDir == FORWARD:
            print('Turn left forward')
        if driveDir == BACKWARD:
            print('Turn left backward')
    if turnDir == RIGHT:
        if driveDir == FORWARD:
            print('Turn right forward')
        if driveDir == BACKWARD:
            print('Turn right backward')
    global he_count
    he_count = 0
    if turnDir == LEFT:
        pi.set_servo_pulsewidth(steering_pin, LEFT_STEERING)
    if turnDir == RIGHT:
        pi.set_servo_pulsewidth(steering_pin, RIGHT_STEERING)

    while(he_count < HE_TICKS_IN_TURN):
        if (ultrasonicDist < 50):
            waitObstacle()
        if driveDir == FORWARD:
            pi.set_PWM_dutycycle(drive_forward_pin, CONSTANT_MOTOR)
            pi.set_PWM_dutycycle(drive_backward_pin, 0)
        if driveDir == BACKWARD:
            pi.set_PWM_dutycycle(drive_forward_pin, 0)
            pi.set_PWM_dutycycle(drive_backward_pin, CONSTANT_MOTOR)


# Drive function for testing navigation
# def drive(direction, axis, targetX, targetY):
#     if direction == FORWARD:
#         if axis == HORIZONTAL:
#             print('Drive forward horizontal')
#             if orientation == FORWARD:
#                 while posX < targetX:
#                     pass
#             if orientation == BACKWARD:
#                 while posX > targetX:
#                     pass
#         if axis == VERTICAL:
#             print('Drive forward vertical')
#             while posY < targetY:
#                 pass
#     if direction == BACKWARD:
#         if axis == HORIZONTAL:
#             print('Drive backward horizontal')
#             if orientation == FORWARD:
#                 while posX > targetX:
#                     pass
#             if orientation == BACKWARD:
#                 while posX < targetX:
#                     pass
#         if axis == VERTICAL:
#             print('Drive backward vertical')
#             while posY > targetY:
#                 pass

def drive(direction, axis, targetX, targetY):
    if (ultrasonicDist < 50):
        waitObstacle()
    condition = True
    angleErrorIntegral = 0
    while condition:
        if direction == FORWARD:
            if axis == HORIZONTAL:
                if orientation == FORWARD:
                    condition = posX < targetX
                if orientation == BACKWARD:
                    condition = posX > targetX
            if axis == VERTICAL:
                condition = posY < targetY
        if direction == BACKWARD:
            if axis == HORIZONTAL:
                if orientation == FORWARD:
                    condition = posX > targetX
                if orientation == BACKWARD:
                    condition = posX < targetX
            if axis == VERTICAL:
                condition = posY > targetY

        posError = 0
        targetAngle = 0
        if axis == HORIZONTAL:
            if orientation == FORWARD:
                posError = -(targetY - posY)
                targetAngle = 0
            if orientation == BACKWARD:
                posError = targetY - posY
                targetAngle = 180
        if axis == VERTICAL:
            posError = targetX - posX
            targetAngle = 270

        angleErrorPlus = 0
        angleErrorMin = 0
        angle = bno.euler[0]

        if type(angle) != float:
            continue

        if targetAngle > angle:
            angleErrorPlus = targetAngle - angle
            angleErrorMin = 360 - targetAngle + angle
        else:
            angleErrorPlus = 360 - angle + targetAngle
            angleErrorMin = angle - targetAngle

        angleError = 0
        if angleErrorPlus < angleErrorMin:
            angleError = angleErrorPlus
        else:
            angleError = -angleErrorMin

        if direction == BACKWARD:
            angleError = -angleError
        angleErrorIntegral += angleError
        driveOutput = CONSTANT_MOTOR

        steerOutput = STRAIGHT_STEERING + KP_STEER_ANGLE*angleError + KI_STEER_ANGLE*angleErrorIntegral + KP_STEER_POS*pow(posError, 3) # Position will only matter when straying very far
        if steerOutput < MIN_STRAIGHT_ADJUST:
            steerOutput = MIN_STRAIGHT_ADJUST
        if steerOutput > MAX_STRAIGHT_ADJUST:
            steerOutput = MAX_STRAIGHT_ADJUST

        if direction == FORWARD:
            pi.set_PWM_dutycycle(drive_forward_pin, driveOutput)
            pi.set_PWM_dutycycle(drive_backward_pin, 0)
        if direction == BACKWARD:
            pi.set_PWM_dutycycle(drive_forward_pin, 0)
            pi.set_PWM_dutycycle(drive_backward_pin, driveOutput)
        
        pi.set_servo_pulsewidth(steering_pin, steerOutput)
        time.sleep(20/1000)

def waitObstacle():
    return()
    stop()
    # Path needs to be clear for 1.5 seconds
    while ultrasonicDist < 50:
        while ultrasonicDist < 50:
            time.sleep(0.5)
        time.sleep(1.5)

def stopReverse():
    pi.set_servo_pulsewidth(steering_pin, STRAIGHT_STEERING)
    pi.set_PWM_dutycycle(drive_forward_pin, CONSTANT_MOTOR)
    pi.set_PWM_dutycycle(drive_backward_pin, 0)
    time.sleep(0.2)
    pastSpeed = speed
    while not speed > pastSpeed:
        pastSpeed = speed

def stop():
    pi.set_PWM_dutycycle(drive_forward_pin, 0)
    pi.set_PWM_dutycycle(drive_backward_pin, 0)

he_pin = 17
drive_forward_pin = 26
drive_backward_pin = 20
steering_pin = 5
us_trig_pin = 25
us_echo_pin = 8

# Hall effect sensor
pi.set_glitch_filter(he_pin, 100)
pi.callback(he_pin, pigpio.RISING_EDGE, HE_callback)

# Motor driver PWM
pi.set_PWM_frequency(drive_forward_pin, 8000)
pi.set_PWM_frequency(drive_backward_pin, 8000)
pi.set_PWM_dutycycle(drive_forward_pin, 0)
pi.set_PWM_dutycycle(drive_backward_pin, 0)
# Steering servo PWM
pi.set_servo_pulsewidth(steering_pin, STRAIGHT_STEERING)

# Set up IMU
class BNO055_extended(adafruit_bno055.BNO055_I2C):
    def set_calibration(self, data):
        """Set the sensor's calibration data using a list of 22 bytes that
        represent the sensor offsets and calibration data.  This data should be
        a value that was previously retrieved with get_calibration (and then
        perhaps persisted to disk or other location until needed again).
        """        
        # Check that 22 bytes were passed in with calibration data.
        if data is None or len(data) != 22:
            raise ValueError('Expected a list of 22 bytes for calibration data.')
        # Switch to configuration mode, as mentioned in section 3.10.4 of datasheet.
        self.mode = adafruit_bno055.CONFIG_MODE
        # Set the 22 bytes of calibration data.
        self._write_register_data(0X55, data)
        # Go back to normal operation mode.
        self.mode = adafruit_bno055.NDOF_MODE
    
    def _write_register_data(self, register, data):
        write_buffer = bytearray(1)
        write_buffer[0] = register & 0xFF
        write_buffer[1:len(data)+1]=data
        with self.i2c_device as i2c:
            i2c.write(write_buffer, start=0, end=len(write_buffer))

i2c = board.I2C()
bno = BNO055_extended(i2c)
bno.mode = adafruit_bno055.IMUPLUS_MODE
bno.set_calibration([251, 255, 212, 255, 236, 255, 0, 0, 0, 0, 0, 0, 255, 255, 255, 255, 255, 255, 232, 3, 0, 0])

# Start ultrasonic sensor thread
ultrasonic_thread = Thread(target=ultrasonicReader)
ultrasonic_thread.daemon = True
ultrasonic_thread.start()

# Start scale thread
scale_thread = Thread(target=scaleReader)
scale_thread.daemon = True
scale_thread.start()

# Start position receiving thread
dwm_thread = Thread(target=receive_position)
dwm_thread.daemon = True
dwm_thread.start()
def cleanup():
    print("Exiting")
    ser.write("\r".encode()) 
    ser.close()
    stop()
    pi.stop()
    GPIO.cleanup()

atexit.register(cleanup)
time.sleep(2.5)

# Test various sensors
while False:
    print("X:", posX, " Y:", posY)
    print('Ultrasonic:', ultrasonicDist)
    print('Speed:', speed)
    print('Weight:', weight)
    print('Direction', bno.euler[0])
    print('')
    time.sleep(1)

homeX = 21#-1
homeY = 21.5
currentX = homeX

state = IDLE
while (True):
    # Idle at home

    # Wait for voice input (call to desk)
    #
    #
    #
    time.sleep(3)
    #
    #
    destination = '405' # Destination bench will be stored in this variable
    state = GETTING_MESSAGE


    destX = benchX[destination]
    destY = benchY[destination]

    if (destX <= posX):
        if orientation == FORWARD:
            drive(BACKWARD, HORIZONTAL, targetX=destX-TURN_MARGIN+1, targetY=homeY) # Drive backwards until slightly passed row
            stopReverse()
            turn(LEFT, FORWARD) # Turn left
        else:
            drive(FORWARD, HORIZONTAL, targetX=destX+TURN_MARGIN, targetY=homeY) # Drive forwards until reach row
            turn(RIGHT, FORWARD) # Turn right
            orientation = FORWARD
    else:
        if orientation == FORWARD:
            drive(FORWARD, HORIZONTAL, targetX=destX-TURN_MARGIN, targetY=homeY) # Drive forwards until reach row
            turn(LEFT, FORWARD) # Turn left
        else:
            drive(BACKWARD, HORIZONTAL, targetX=destX+TURN_MARGIN-1, targetY=homeY) # Drive backwards until slightly passed row
            stopReverse()
            turn(RIGHT, FORWARD) # Turn right
            orientation = FORWARD

    drive(FORWARD, VERTICAL, targetX=destX, targetY=destY) # Drive forward to bench
    stop()
    currentX = destX

    # Visit benches and ask for input until idle
    while state != IDLE:
        if state == GETTING_MESSAGE:
            # Wait for voice input (get action)
            #
            # Use ear scrip
            #
            #
            #
            time.sleep(3)
            # old_ear.py will give these three inputs
            failed = False
            command = 'Deliver' # Command will be 'Deliver' or 'Request'
            destination = '407'

            if failed:
                state = IDLE
            else:
                if command == 'Deliver':
                    while weight < SCALE_THRESHOLD:     
                        time.sleep(0.5)
                    state = DELIVERING
                if command == 'Fetch':
                    state = FETCHING_1
        if state == DELIVERING:
            while weight < SCALE_THRESHOLD:
                time.sleep(0.5)
            state = IDLE
        if state == FETCHING_1:
            # Say what we are fetching
            #
            #
            #
            while weight < SCALE_THRESHOLD:
                time.sleep(0.5)
            state = FETCHING_2
        if state == FETCHING_2:
            while weight >= SCALE_THRESHOLD:
                time.sleep(0.5)
            state = IDLE
        
        time.sleep(1.5)

        if state != IDLE:
            destX = benchX[destination]
            destY = benchY[destination]

            if destX == currentX:
                if destY > posY:
                    drive(FORWARD, VERTICAL, targetX=destX, targetY=destY) # Drive forwards until close to destination
                else:
                    drive(BACKWARD, VERTICAL, targetX=destX, targetY=destY) # Drive backwards until close to destination
            else:
                drive(BACKWARD, VERTICAL, targetX=currentX, targetY=homeY+TURN_MARGIN+3) # Drive backwards to line

                if destX < currentX:
                    turn(RIGHT, BACKWARD)
                    stopReverse()
                    orientation = BACKWARD
                    drive(FORWARD, HORIZONTAL, targetX=destX+TURN_MARGIN, targetY=homeY) # Drive forwards until reach row
                    turn(RIGHT, FORWARD)
                    orientation = FORWARD
                else:
                    turn(LEFT, BACKWARD)
                    stopReverse()
                    orientation = FORWARD
                    drive(FORWARD, HORIZONTAL, targetX=destX-TURN_MARGIN, targetY=homeY) # Drive forwards until reach row
                    turn(LEFT, FORWARD)

                drive(FORWARD, VERTICAL, targetX=destX, targetY=destY) # Drive forward to bench

            currentX = destX

        # Go home when no more destinations
        drive(BACKWARD, VERTICAL, targetX=currentX, targetY=homeY+TURN_MARGIN) # Drive backwards to line
        if homeX < posX:
            turn(RIGHT, BACKWARD)
            stopReverse()
            orientation = BACKWARD
            drive(FORWARD, HORIZONTAL, targetX=homeX, targetY=homeY) # Drive forward to home
        else:
            turn(LEFT, BACKWARD)
            stopReverse()
            orientation = FORWARD
            drive(FORWARD, HORIZONTAL, targetX=homeX, targetY=homeY) # Drive forward to home
        stop()