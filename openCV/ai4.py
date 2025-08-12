import cv2
import time
from datetime import datetime, timedelta
import os
import sys
import Jetson.GPIO as GPIO

# --- Parametry kamery ---
w = 3264
h = 2464
flip = 0
output_dir = "/home/arkadiusz/Desktop/captured_images"
os.makedirs(output_dir, exist_ok=True)

# --- Znajdź numerację startową ---
existing = sorted([f for f in os.listdir(output_dir) if f.endswith(".jpg")])
if existing:
    last_num = int(existing[-1].split("_")[1])
else:
    last_num = 0

max_images = 10
count = 0
log_filename = None

# --- Konfiguracja GStreamer ---
camSet = (
    "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3264, height=2464,"
    + " format=NV12, framerate=21/1 ! nvvidconv flip-method="
    + str(flip)
    + " ! video/x-raw, width="
    + str(w)
    + ", height="
    + str(h)
    + ", format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
)

print("⏳ Czekam 5 s na stabilizację systemu...")
time.sleep(5)

cam = cv2.VideoCapture(camSet)
if not cam.isOpened():
    print("❌ Nie można otworzyć kamery!")
    exit()

print("✅ Kamera otwarta. Rozpoczynam zapis...")

try:
    while count < max_images:
        count += 1
        last_num += 1

        ret, frame = cam.read()
        if not ret:
            print("❌ Błąd podczas odczytu klatki.")
            break

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"{timestamp}_{last_num:04d}_{timestamp[-6:]}.jpg")

        # Ustal log_filename przy pierwszym zdjęciu
        if log_filename is None:
            parts = filename.rsplit('_', 2)  # ["20250810", "0042", "153045.jpg"]
            time_str = parts[2].split('.')[0]  # "153045"
            time_obj = datetime.strptime(time_str, "%H%M%S") - timedelta(seconds=1)
            new_time_str = time_obj.strftime("%H%M%S")
            log_filename = os.path.join(output_dir, f"{parts[0]}_{parts[1]}_{new_time_str}.txt")

            # --- Przekierowanie logów ---
            log_file = open(log_filename, "a")
            sys.stdout = log_file
            sys.stderr = log_file
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Start sesji, pierwszy plik: {filename}")

        cv2.imwrite(filename, frame)
        print(f"💾 Zapisano: {filename}")

        time.sleep(1)

except Exception as e:
    print(f"❌ Błąd: {e}")

finally:
    cam.release()
    print("📷 Kamera zamknięta.")

    # Przywrócenie std output
    if log_filename:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Koniec programu")
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        log_file.close()

    # Czyszczenie GPIO
    try:
        GPIO.cleanup()
    except Exception as e:
        print(f"⚠️ Błąd czyszczenia GPIO: {e}")
