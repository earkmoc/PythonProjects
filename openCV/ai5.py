import cv2
import time
from datetime import datetime, timedelta
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
    aheadLeft = count in [0, 1, 3, 4, 6, 7, 8, 9]
    aheadRight = count in [0, 1, 2, 4, 5, 8, 9]
    Left()
    Right()


def Stop():
    GPIO.output([IN1, IN2, IN3, IN4], (GPIO.LOW, GPIO.LOW, GPIO.LOW, GPIO.LOW))


def Left():
    if aheadLeft:
        GPIO.output([IN1, IN2], (GPIO.HIGH, GPIO.LOW))
    else:
        GPIO.output([IN1, IN2], (GPIO.LOW, GPIO.HIGH))


def Right():
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
w, h, flip = 1920, 1080, 0   # zmniejszona rozdzielczość
max_images = 10
delay_start = 5
output_dir = "/home/arkadiusz/Desktop/captured_images"
os.makedirs(output_dir, exist_ok=True)

print(f"⏳ Czekam {delay_start} s na stabilizację systemu...")
time.sleep(delay_start)

# --- Znajdź najwyższy numer w katalogu ---
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

# --- Ustawienia kamery ---
camSet = (
    f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1920, height=1080,"
    f" format=NV12, framerate=21/1 ! nvvidconv flip-method={flip}"
    f" ! video/x-raw, width={w}, height={h}, format=BGRx ! videoconvert"
    f" ! video/x-raw, format=BGR ! appsink"
)
cam = cv2.VideoCapture(camSet)
if not cam.isOpened():
    print("❌ Nie można otworzyć kamery!")
    GPIO.cleanup()
    exit()

count4Run = 0
log_filename = None
prev_time = time.time()

while count4Run < max_images:
    ret, frame = cam.read()
    if not ret or frame is None or frame.size == 0:
        if log_filename:
            with open(log_filename, "a") as f:
                f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | ⚠️ Pominięto zdjęcie (brak danych z kamery)\n")
        continue

    count4Run += 1
    count4Folder += 1
    current_time = datetime.now().strftime("%H%M%S")
    filename = os.path.join(output_dir, f"{session_date}_{count4Folder:04d}_{current_time}.jpg")
    cv2.imwrite(filename, frame)

    if log_filename is None:
        parts = filename.rsplit('_', 2)
        time_str = parts[2].split('.')[0]
        time_obj = datetime.strptime(time_str, "%H%M%S") - timedelta(seconds=1)
        new_time_str = time_obj.strftime("%H%M%S")
        log_filename = os.path.join(output_dir, f"{parts[0]}_{parts[1]}_{new_time_str}.txt")

        with open(log_filename, "a") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | Start sesji, pierwszy plik: {filename}\n")

    cycle_duration = time.time() - prev_time
    prev_time = time.time()

    with open(log_filename, "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | Zapisano {filename} | Czas od poprzedniego zdjęcia: {cycle_duration:.2f}s\n")

    Start(count4Run)
    time.sleep(3)
    Stop()

cam.release()
Stop()
GPIO.cleanup()

print(f"✅ Sesja zakończona. Log zapisany w: {log_filename}")
