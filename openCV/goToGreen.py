# sudo nano /etc/systemd/system/myscript.service
# sudo chmod 644 /etc/systemd/system/myscript.service
# sudo systemctl daemon-reexec
# sudo systemctl daemon-reload
# sudo systemctl enable myscript.service
# sudo systemctl start myscript.service

import os
import re
import sys
import cv2
import time
from datetime import datetime, timedelta
import math
import numpy as np
import Jetson.GPIO as GPIO

red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
yellow = (0, 255, 255)

delay_start = 5
print(f"⏳ Czekam {delay_start} s na stabilizację systemu...")
time.sleep(delay_start)

start_time = datetime.now()
limit_duration = timedelta(minutes=5)

log_filename = None
output_dir = "/home/arkadiusz/Desktop/captured_images"
os.makedirs(output_dir, exist_ok=True)

pattern = re.compile(
    r"^(\d{8})_(\d+)_"
    r"(\d+)-(\d+)-(\d+) "
    r"(\d+):(\d+):(\d+)"
    r"(?:\.(\d+))?"     # ← opcjonalne milisekundy
    r"\.jpg$"
)

max_num = 0
for fname in os.listdir(output_dir):
    match = pattern.match(fname)
    if match:
        num = int(match.group(2))
        if num > max_num:
            max_num = num

count4Folder = max_num
session_date = datetime.now().strftime("%Y%m%d")
count4Folder += 1


def NowStr():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def ImgFileName():
    return os.path.join(output_dir, f"{session_date}_{count4Folder:04d}_{NowStr()}.jpg")


filename = ImgFileName()

if log_filename is None:
    log_filename = os.path.join(output_dir, f"{filename.split('.')[0]}.txt")

    # --- Przekierowanie logów ---
    log_file = open(log_filename, "a")
    sys.stdout = log_file
    sys.stderr = log_file
    print(f"{NowStr()} | Start sesji")

print(os.path.exists("/tmp/.X11-unix"))
# if os.path.exists("/tmp/.X11-unix"):
# exit(0)

# --- Ustawienia GPIO ---
IN1 = 29
IN2 = 31
ENA = 32
ENB = 33
IN3 = 35
IN4 = 36
speed = 100
prevState = "stop"


def SetPrevState(state):
    global prevState
    prevState = state


def TurnEnginesOff(timeStr):
    GPIO.output([IN1, IN2, IN3, IN4], (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))
    print(timeStr, prevState, 'stop')
    SetPrevState("stop")


def TurnEnginesOn(timeStr):
    SetLeftWheels(True)
    SetRightWheels(True)
    print(timeStr, prevState, 'start')
    SetPrevState("start")


def TurnEnginesBack(timeStr):
    SetLeftWheels(False)
    SetRightWheels(False)
    print(timeStr, prevState, 'back')
    SetPrevState("back")


def TurnLeft(timeStr):
    SetLeftWheels(True)
    SetRightWheels(False)
    print(timeStr, prevState, 'left')
    SetPrevState("left")


def TurnRight(timeStr):
    SetLeftWheels(False)
    SetRightWheels(True)
    print(timeStr, prevState, 'right')
    SetPrevState("right")


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
w, h, flip = 640, 480, 0
delay_start = 5
esc = 27

print(f"⏳ Czekam {delay_start} s na stabilizację systemu...")
time.sleep(delay_start)

camSet = (
    f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3264, height=2464,"
    f" format=NV12, framerate=21/1 ! nvvidconv flip-method={flip}"
    f" ! video/x-raw, width=3264, height=2464, format=BGRx ! videoconvert"
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

        if cv2.waitKey(1) == esc:
            break

        if datetime.now() - start_time >= limit_duration:
            break

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
        cv2.rectangle(frame, (0, 0), (w, 80), (0, 0, 0), -1)

        # hide the weels
        radius = 120
        dw = 70
        dh = 20
        wheel1x = 0 + dw + 44
        wheel1y = h - dh
        wheel2x = w - dw - 54
        wheel2y = h - dh
        cv2.circle(frame, (wheel1x, wheel1y), radius, (0, 0, 0), -1)
        cv2.circle(frame, (wheel2x, wheel2y), radius, (0, 0, 0), -1)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        HueMask = CreateFGMask(hsv)
        v_channel = hsv[:, :, 2]
        v_masked = cv2.bitwise_and(v_channel, v_channel, mask=HueMask)
        _, FGMask_HSV_Otsu = cv2.threshold(v_masked, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(FGMask_HSV_Otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        aimX, aimY = (int)(w/2), h - 30
        min_distance = float("inf")
        distance_thresold = 20
        closest_center = None

        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area >= 200:
                x, y, ww, hh = cv2.boundingRect(contour)
                rect_center_x = int(x + ww / 2)
                rect_center_y = int(y + hh / 2)

                cv2.drawContours(frame, [contour], -1, blue, 3)
                cv2.rectangle(frame, (x, y), (x+ww, y+hh), red, 2)
                cv2.putText(frame, f"{i}", ((rect_center_x, rect_center_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, green, 2)

                distance = math.hypot(aimX - rect_center_x, aimY - rect_center_y)
                if distance < min_distance and distance > distance_thresold:
                    min_distance = distance
                    closest_center = (rect_center_x, rect_center_y)
                    closest_contour_id = i

        # aim
        cv2.rectangle(frame, (aimX - 3, aimY - 3), (aimX + 3, aimY + 3), green, 1)

        tolerance = 60
        if closest_center:
            cv2.line(frame, (aimX, aimY), closest_center, yellow, 1)
            filename = ImgFileName()
            print(NowStr(), filename)
            if cv2.imwrite(filename, frame):
                with open(filename, "rb") as f:
                    f.flush
                    os.fsync(f.fileno())
            count4Folder += 1

            dx = closest_center[0] - aimX
            print(NowStr(), closest_contour_id, closest_center, dx, min_distance)
            if dx < -tolerance:
                if prevState == "right":
                    TurnEnginesOn(NowStr())
                    time.sleep(1)
                else:
                    TurnLeft(NowStr())
            elif dx > tolerance:
                if prevState == "left":
                    TurnEnginesOn(NowStr())
                    time.sleep(1)
                else:
                    TurnRight(NowStr())
            else:
                TurnEnginesOn(NowStr())
        else:
            TurnEnginesOff(NowStr())

        # time.sleep(1)

except Exception as e:
    print(f"❌ Błąd: {e}")

finally:
    TurnEnginesOff(NowStr())
    cam.release()
    GPIO.cleanup()

print(f"✅ Sesja zakończona. Log zapisany w: {log_filename}")

if log_filename:
    print(f"{NowStr()} | Koniec programu")
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    log_file.close()
