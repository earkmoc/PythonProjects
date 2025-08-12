#!/usr/bin/env python

# https://pypi.org/project/Jetson.GPIO/
import Jetson.GPIO as GPIO
import numpy as np
import cv2

esc = 27
keyA = 97
keyC = 99
keyD = 100
keyS = 115
keyW = 119
keyX = 120
keyZ = 122

IN1 = 29
IN2 = 31
ENA = 32
ENB = 33
IN3 = 35
IN4 = 36

flip = 0

w = 320
h = 240
red = (0, 0, 255)
green = (0, 255, 0)
aheadLeft = True
aheadRight = True
speed = 50


def window(img, name, c, r):
    cv2.imshow(name, img)
    cv2.moveWindow(name, 100 + c * w, 50 + r * (h + 28))


def OpositeLeft():
    global aheadLeft
    aheadLeft = not aheadLeft
    print("oposite")
    Left()


def OpositeRight():
    global aheadRight
    aheadRight = not aheadRight
    print("oposite")
    Right()


def Left():
    global aheadLeft
    if aheadLeft:
        GPIO.output([IN1, IN2], (GPIO.HIGH, GPIO.LOW))
    else:
        GPIO.output([IN1, IN2], (GPIO.LOW, GPIO.HIGH))
    print("lewy")


def Right():
    global aheadRight
    if aheadRight:
        GPIO.output([IN3, IN4], (GPIO.HIGH, GPIO.LOW))
    else:
        GPIO.output([IN3, IN4], (GPIO.LOW, GPIO.HIGH))
    print("prawy")


def Stop():
    global speed
    speed = 0
    # pwm.ChangeDutyCycle(speed)
    # pwmB.ChangeDutyCycle(speed)
    GPIO.output([IN1, IN2, IN3, IN4], (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))
    print("stop")


def Faster():
    global speed
    speed += 10
    if speed > 100:
        speed = 100
    print(speed)
    pwm.ChangeDutyCycle(speed)
    # pwmB.ChangeDutyCycle(speed)


def Slower():
    global speed
    speed -= 10
    if speed < 0:
        speed = 0
    print(speed)
    pwm.ChangeDutyCycle(speed)
    # pwmB.ChangeDutyCycle(speed)


mainWindowName = 'nanoCam'
cv2.namedWindow(mainWindowName)
frame = np.zeros((1, 1500, 3), dtype=np.uint8)
window(frame, mainWindowName, 0, 3)

GPIO.setmode(GPIO.BOARD)
GPIO.setup([ENA, IN1, IN2, IN3, IN4, ENB], GPIO.OUT)

pwm = GPIO.PWM(ENA, 50)
pwm.start(speed)

pwmB = GPIO.PWM(ENB, 50)
pwmB.start(speed)

GPIO.output([IN1, IN2, IN3, IN4], (GPIO.HIGH, GPIO.LOW, GPIO.HIGH, GPIO.LOW))

while True:
    key = cv2.waitKey(1)
    if key == esc:
        break

    if key > -1:
        print(key)

    if key == keyA:
        Left()
    if key == keyD:
        Right()
    if key == keyS:
        Stop()
    if key == keyW:
        Faster()
    if key == keyX:
        Slower()
    if key == keyZ:
        OpositeLeft()
    if key == keyC:
        OpositeRight()

GPIO.output([IN1, IN2, IN3, IN4], (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))

# pwm.ChangeDutyCycle(100)
# time.sleep(2)

# pwm.ChangeDutyCycle(0)
# pwmB.ChangeDutyCycle(0)

pwm.stop()
# pwmB.stop()

GPIO.cleanup([ENA, IN1, IN2, IN3, IN4, ENB])

# https://github.com/NVIDIA/jetson-gpio/issues/20

# sudo usermod -aG gpio $USER
# sudo chown root.gpio /dev/gpiochip0
# sudo chmod 660 /dev/gpiochip0
# sudo chown root.gpio /dev/gpiochip1
# sudo chmod 660 /dev/gpiochip1

# sudo nano /etc/udev/rules.d/99-gpio.rules
# SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c '\
# chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio;\
# chown -R root:gpio /dev/gpiochip0 && chmod -R 660 /dev/gpiochip0\
# '"
# sudo usermod -aG gpio $USER
