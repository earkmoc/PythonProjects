import cv2
import time
from datetime import datetime
import os
import re
import Jetson.GPIO as GPIO

# --- Ustawienia GPIO ---
IN1 = 29
IN2 = 31
ENA = 32
ENB = 33
IN3 = 35
IN4 = 36
speed = 100
aheadLeft = True
aheadRight = True

def Start(count):
    global aheadLeft, aheadRight
    aheadLeft = count in range(10)
    aheadRight = count in range(10)
    Left()
    Right()

def Stop():
    GPIO.output([IN1, IN2, IN3, IN4], (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))

def Left():
    global aheadLeft
    if aheadLeft:
        GPIO.output([IN1, IN2], (GPIO.HIGH, GPIO.LOW))
    else:
        GPIO.output([IN1, IN2], (GPIO.LOW, GPIO.HIGH))

def Right():
    global aheadRight
    if aheadRight:
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
w, h, flip = 3264, 2464, 0
max_images = 10
delay_start = 5
output_dir = "/home/arkadiusz/Desktop/captured_images"
os.makedirs(output_dir, exist_ok=True)

print(f"⏳ Czekam {delay_start} s na stabilizację systemu...")
time.sleep(delay_start)

pattern = re.compile(r"^\d{8}_(\d+)_\d{6}\.jpg$")
max_num = 0
for fname in os.listdir(output_dir):
    match = pattern.match(fname)
    if match:
        num = int(match.group(1))
        if num > max_num:
            max_num = num
count4Folder = max_num

session_date = datetime.now().strftime("%Y%m%d")

camSet = (
    "nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464,"
    " format=NV12, framerate=21/1 ! nvvidconv flip-method="
    + str(flip)
    + " ! video/x-raw, width="
    + str(w)
    + ", height="
    + str(h)
    + ", format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
)
cam = cv2.VideoCapture(camSet)
if not cam.isOpened():
    print("Nie można otworzyć kamery!")
    exit()

count4Run = 0
log_filename = None
prev_time = time.time()

while count4Run < max_images:
    ret, frame = cam.read()
    if not ret or frame is None or frame.size == 0:
        if log_filename:
            with open(log_filename, "a") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ⚠️ Pominięto zdjęcie (brak danych z kamery)\n")
        continue

    count4Run += 1
    count4Folder += 1
    current_time = datetime.now().strftime("%H%M%S")
    filename = os.path.join(output_dir, f"{session_date}_{count4Folder:04d}_{current_time}.jpg")
    cv2.imwrite(filename, frame)

    if log_filename is None:
        log_filename = filename.rsplit('.', 1)[0] + ".txt"
        with open(log_filename, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Start sesji, pierwszy plik: {filename}\n")

    cycle_duration = time.time() - prev_time
    prev_time = time.time()

    with open(log_filename, "a") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Zapisano {filename} | Czas od poprzedniego zdjęcia: {cycle_duration:.2f}s\n")

    Start(count4Run)
    time.sleep(3)
    Stop()

cam.release()
Stop()
pwm.stop()
GPIO.cleanup([ENA, IN1, IN2, IN3, IN4, ENB])

print(f"✅ Sesja zakończona. Log zapisany w: {log_filename}")
