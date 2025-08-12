import cv2
import time
from datetime import datetime
import os
import re

# PARAMETRY KAMERY
w = 3264
h = 2464
flip = 0
max_images = 10  # ile zdjęć zrobić w tej sesji
delay_start = 5  # sekundy opóźnienia po starcie

# Folder docelowy
output_dir = "/home/arkadiusz/Desktop/captured_images"
os.makedirs(output_dir, exist_ok=True)

# Opóźnienie startu
print(f"⏳ Czekam {delay_start} s na stabilizację systemu...")
time.sleep(delay_start)

# Wzorzec do wyciągania numeru pliku
pattern = re.compile(r"^\d{8}_(\d+)_\d{6}\.jpg$")

# Znajdź najwyższy numer w folderze
max_num = 0
for fname in os.listdir(output_dir):
    match = pattern.match(fname)
    if match:
        num = int(match.group(1))
        if num > max_num:
            max_num = num

print(f"📂 Ostatni numer w folderze: {max_num}")
count = max_num

# Data sesji
session_date = datetime.now().strftime("%Y%m%d")

# Ustawienia kamery
camSet = (
    "nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464,"
    + " format=NV12, framerate=21/1 ! nvvidconv flip-method="
    + str(flip)
    + " ! video/x-raw, width="
    + str(w)
    + ", height="
    + str(h)
    + ", format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
)

# Otwórz kamerę
cam = cv2.VideoCapture(camSet)
if not cam.isOpened():
    print("❌ Nie można otworzyć kamery!")
    exit()

print("✅ Kamera otwarta. Rozpoczynam zapis...")

# Pętla zapisu zdjęć
for _ in range(max_images):
    count += 1

    ret, frame = cam.read()
    if not ret:
        print("❌ Błąd odczytu klatki.")
        break

    current_time = datetime.now().strftime("%H%M%S")
    filename = os.path.join(output_dir, f"{session_date}_{count:04d}_{current_time}.jpg")

    cv2.imwrite(filename, frame)
    print(f"💾 Zapisano: {filename}")

    time.sleep(1)

# Zamknij kamerę
cam.release()
print("📷 Kamera zamknięta.")
