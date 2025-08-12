import cv2
import time
from datetime import datetime
import os
import re
import Jetson.GPIO as GPIO

# ==== KONFIGURACJA RUCHU ====
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
    aheadLeft = count in range(0, 10)
    aheadRight = count in range(0, 10)
    Left()
    Right()

def Stop():
    GPIO.output([IN1, IN2, IN3, IN4], (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))

def Left():
    GPIO.output([IN1, IN2], (GPIO.HIGH, GPIO.LOW) if aheadLeft else (GPIO.LOW, GPIO.HIGH))

def Right():
    GPIO.output([IN3, IN4], (GPIO.HIGH, GPIO.LOW) if aheadRight else (GPIO.LOW, GPIO.HIGH))

GPIO.setmode(GPIO.BOARD)
GPIO.setup([ENA, IN1, IN2, IN3, IN4, ENB], GPIO.OUT)

pwm = GPIO.PWM(ENA, 50)
pwm.start(speed)
pwmB = GPIO.PWM(ENB, 50)
pwmB.start(speed)

# ==== KONFIGURACJA KAMERY ====
w = 1920
h = 1080
flip = 0
max_images = 10
delay_start = 5

output_dir = "/home/arkadiusz/Desktop/captured_images"
os.makedirs(output_dir, exist_ok=True)

log_file = os.path.join(output_dir, "capture_log.txt")
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

log(f"=== Start sesji ===")
time.sleep(delay_start)

# ==== KONTYNUACJA NUMERACJI ====
pattern = re.compile(r"^\d{8}_(\d+)_\d{6}\.jpg$")
max_num = 0
for fname in os.listdir(output_dir):
    match = pattern.match(fname)
    if match:
        num = int(match.group(1))
        if num > max_num:
            max_num = num
count4Folder = max_num

# Data sesji
session_date = datetime.now().strftime("%Y%m%d")

# Kamera
camSet = (
    f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width={w}, height={h},"
    f" format=NV12, framerate=21/1 ! nvvidconv flip-method={flip} ! "
    f"video/x-raw, width={w}, height={h}, format=BGRx ! videoconvert ! "
    f"video/x-raw, format=BGR ! appsink"
)
cam = cv2.VideoCapture(camSet)
if not cam.isOpened():
    log("❌ Nie udało się otworzyć kamery.")
    exit()

count4Run = 0
prev_time = time.time()

while count4Run < max_images:
    start_cycle = time.time()
    
    ret, frame = cam.read()
    if ret and frame is not None and frame.size > 0:
        count4Run += 1
        count4Folder += 1
        current_time = datetime.now().strftime("%H%M%S")
        filename = os.path.join(output_dir, f"{session_date}_{count4Folder:04d}_{current_time}.jpg")
        cv2.imwrite(filename, frame)
        cycle_duration = time.time() - prev_time
        log(f"💾 Zapisano {filename} | Czas od poprzedniego zdjęcia: {cycle_duration:.2f}s")
        prev_time = time.time()
    else:
        log(f"⚠️ Pominięto plik {count4Folder+1:04d} (brak danych z kamery).")
        continue

    Start(count4Run)
    time.sleep(3)
    Stop()

# Zwolnij zasoby
cam.release()
Stop()
pwm.stop()
pwmB.stop()
GPIO.cleanup([ENA, IN1, IN2, IN3, IN4, ENB])

log(f"=== Koniec sesji ===")
