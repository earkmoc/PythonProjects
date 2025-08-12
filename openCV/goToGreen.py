# sudo nano /etc/systemd/system/myscript.service
# sudo chmod 644 /etc/systemd/system/myscript.service
# sudo systemctl daemon-reexec
# sudo systemctl daemon-reload
# sudo systemctl enable myscript.service
# sudo systemctl start myscript.service

import cv2
import time
import math
import numpy as np
import Jetson.GPIO as GPIO

# Environment=DISPLAY=:0
# if bool(os.environ.get("DISPLAY")):
# exit(0)

# --- Ustawienia GPIO ---
IN1 = 29
IN2 = 31
ENA = 32
ENB = 33
IN3 = 35
IN4 = 36
speed = 100


def TurnEnginesOff():
    GPIO.output([IN1, IN2, IN3, IN4], (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))


def TurnEnginesOn():
    SetLeftWheels(True)
    SetRightWheels(True)


def TurnEnginesBack():
    SetLeftWheels(False)
    SetRightWheels(False)


def TurnLeft():
    SetLeftWheels(True)
    SetRightWheels(False)


def TurnRight():
    SetLeftWheels(False)
    SetRightWheels(True)


def SetLeftWheels(ahead):
    if ahead:
        GPIO.output([IN1, IN2], (GPIO.HIGH, GPIO.LOW))
    else:
        GPIO.output([IN1, IN2], (GPIO.LOW, GPIO.HIGH))


def SetRightWheels(ahead):
    if ahead:
        GPIO.output([IN3, IN4], (GPIO.HIGH, GPIO.LOW))
    else:
        GPIO.output([IN3, IN4], (GPIO.LOW, GPIO.HIGH))


GPIO.setmode(GPIO.BOARD)
GPIO.setup([ENA, IN1, IN2, IN3, IN4, ENB], GPIO.OUT)

pwm = GPIO.PWM(ENA, 50)
pwm.start(speed)

pwmB = GPIO.PWM(ENB, 50)
pwmB.start(speed)

# --- Kamera i katalog ---
w, h, flip = 320, 240, 0
delay_start = 5

print(f"⏳ Czekam {delay_start} s na stabilizację systemu...")
time.sleep(delay_start)

camSet = (
    f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3264, height=2464,"
    f" format=NV12, framerate=21/1 ! nvvidconv flip-method={flip}"
    f" ! video/x-raw, width={w}, height={h}, format=BGRx ! videoconvert"
    f" ! video/x-raw, format=BGR ! appsink drop=1 max-buffers=1"
)
cam = cv2.VideoCapture(camSet)
if not cam.isOpened():
    print("Nie można otworzyć kamery!")
    GPIO.cleanup()
    exit()

# image analyse
presets = {
    0: {'name': 'Plant',  'hL': 30,  'hH': 80},
    1: {'name': 'Yellow', 'hL': 9,   'hH': 30},
    2: {'name': 'Red',    'hL': 120, 'hH': 10}
}


def CreateFGMask(hsv):
    p = presets[0]
    hl = p['hL']
    hh = p['hH']
    sl = 0
    sh = 255
    vl = 0
    vh = 255

    if hl < hh:
        hsvl = np.array([hl, sl, vl])
        hsvh = np.array([hh, sh, vh])
        return cv2.inRange(hsv, hsvl, hsvh)

    hl1 = 0
    hh1 = hh
    hsvl1 = np.array([hl1, sl, vl])
    hsvh1 = np.array([hh1, sh, vh])
    FGMask1 = cv2.inRange(hsv, hsvl1, hsvh1)

    hl2 = hl
    hh2 = 179
    hsvl2 = np.array([hl2, sl, vl])
    hsvh2 = np.array([hh2, sh, vh])
    FGMask2 = cv2.inRange(hsv, hsvl2, hsvh2)

    return cv2.add(FGMask1, FGMask2)


try:
    while True:
        ret, frame = cam.read()
        if not ret or frame is None or frame.size == 0:
            continue

        height, width, _ = frame.shape
        wod = (int)(width / 2 - 0.3 * width)
        wdo = (int)(width / 2 + 0.3 * width)
        hod = (int)(height / 2 - 0.25 * height)
        hdo = (int)(height / 2 + 0.38 * height)
        img = frame[hod:hdo, wod:wdo]

        frame = cv2.resize(img, (w, h))

        # hide the horizon
        cv2.rectangle(frame, (0, 0), (w, 40), (0, 0, 0), -1)

        # hide the weels
        radius = 60
        dw = 35
        dh = 9
        wheel1x = 0 + dw + 22
        wheel1y = h - dh
        wheel2x = w - dw - 27
        wheel2y = h - dh
        cv2.circle(frame, (wheel1x, wheel1y), radius, (0, 0, 0), -1)
        cv2.circle(frame, (wheel2x, wheel2y), radius, (0, 0, 0), -1)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        HueMask = CreateFGMask(hsv)
        v_channel = hsv[:, :, 2]
        v_masked = cv2.bitwise_and(v_channel, v_channel, mask=HueMask)
        _, FGMask_HSV_Otsu = cv2.threshold(v_masked, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(FGMask_HSV_Otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        aimX, aimY = (int)(w/2), h - 15
        min_distance = float("inf")
        distance_thresold = 10
        closest_center = None

        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= 50:
                x, y, ww, hh = cv2.boundingRect(contour)
                rect_center_x = int(x + ww / 2)
                rect_center_y = int(y + hh / 2)
                distance = math.hypot(aimX - rect_center_x, aimY - rect_center_y)
                if distance < min_distance and distance > distance_thresold:
                    min_distance = distance
                    closest_center = (rect_center_x, rect_center_y)

        tolerance = 15
        if closest_center:
            dx = closest_center[0] - aimX
            if dx < -tolerance:
                TurnLeft()
            elif dx > tolerance:
                TurnRight()
            else:
                TurnEnginesOn()
        else:
            TurnEnginesOn()

        time.sleep(1)

except Exception as e:
    print(f"❌ Błąd: {e}")

finally:
    TurnEnginesOff()
    cam.release()
    GPIO.cleanup()
