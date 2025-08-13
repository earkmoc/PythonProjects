import os
import cv2
import math
import numpy as np
from datetime import datetime
# import tkinter as tk
# from tkinter import ttk

esc = 27
flip = 0

w = 320
h = 240
red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)
yellow = (0, 255, 255)


def window(img, name, c, r):
    cv2.imshow(name, img)
    cv2.moveWindow(name, 100 + c * w, 50 + r * (h + 28))


def nic(param):
    pass


mainWindowName = 'nanoCam'
cv2.namedWindow(mainWindowName)
# cv2.namedWindow(mainWindowName, cv2.WINDOW_AUTOSIZE)
# cv2.namedWindow(mainWindowName, cv2.WINDOW_NORMAL)
frame = np.zeros((1, 1500, 3), dtype=np.uint8)
window(frame, mainWindowName, 0, 3)

image_files_path = '/home/arkadiusz/Desktop/captured_images/'
image_files = [f for f in os.listdir(image_files_path) if f.lower().endswith(".jpg")]

img_index_state = {'index': -1}
img = None

state = {'last_preset': -1}
presets = {
    0: {'name': 'Plant',  'hL': 30,  'hH': 80},
    1: {'name': 'Yellow', 'hL': 9,   'hH': 30},
    2: {'name': 'Red',    'hL': 120, 'hH': 10}
}

tbnImage = 'image'
cv2.createTrackbar(tbnImage, mainWindowName, 0, len(image_files) - 1, nic)

tbnPreset = 'preset'
cv2.createTrackbar(tbnPreset, mainWindowName, 0, len(presets) - 1, nic)

tbnHL = 'hL'
cv2.createTrackbar(tbnHL, mainWindowName, 120, 179, nic)

tbnHH = 'hH'
cv2.createTrackbar(tbnHH, mainWindowName, 10, 179, nic)

tbnSL = 'sL'
cv2.createTrackbar(tbnSL, mainWindowName, 0, 255, nic)

tbnSH = 'sH'
cv2.createTrackbar(tbnSH, mainWindowName, 255, 255, nic)

tbnVL = 'vL'
cv2.createTrackbar(tbnVL, mainWindowName, 0, 255, nic)

tbnVH = 'vH'
cv2.createTrackbar(tbnVH, mainWindowName, 255, 255, nic)

tbnContourAreaThreshold = 'valCA'
cv2.createTrackbar(tbnContourAreaThreshold, mainWindowName, 50, 5000, nic)


def LoadImageIfChanged(state):
    index = cv2.getTrackbarPos(tbnImage, mainWindowName)
    if state['index'] != index:
        state['index'] = index
        filename = image_files[index]
        print(f"Loading image: {filename}")
        return cv2.imread(image_files_path + filename)
    return None


def TrackbarPresets(state):
    preset_index = cv2.getTrackbarPos(tbnPreset, mainWindowName)

    if state['last_preset'] != preset_index:
        state['last_preset'] = preset_index
        p = presets[preset_index]
        cv2.setTrackbarPos(tbnHL, mainWindowName, p['hL'])
        cv2.setTrackbarPos(tbnHH, mainWindowName, p['hH'])
        # cv2.setTrackbarPos(tbnSL, mainWindowName, p['sL'])
        # cv2.setTrackbarPos(tbnSH, mainWindowName, p['sH'])
        # cv2.setTrackbarPos(tbnVL, mainWindowName, p['vL'])
        # cv2.setTrackbarPos(tbnVH, mainWindowName, p['vH'])
        cv2.setTrackbarPos(tbnSL, mainWindowName, 0)
        cv2.setTrackbarPos(tbnSH, mainWindowName, 255)
        cv2.setTrackbarPos(tbnVL, mainWindowName, 0)
        cv2.setTrackbarPos(tbnVH, mainWindowName, 255)
        print(f"Preset: {p['name']}")


def CreateFGMask(hsv):
    hl = cv2.getTrackbarPos(tbnHL, mainWindowName)
    hh = cv2.getTrackbarPos(tbnHH, mainWindowName)
    sl = cv2.getTrackbarPos(tbnSL, mainWindowName)
    sh = cv2.getTrackbarPos(tbnSH, mainWindowName)
    vl = cv2.getTrackbarPos(tbnVL, mainWindowName)
    vh = cv2.getTrackbarPos(tbnVH, mainWindowName)

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


# camSet = (
#     "nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464,"
#     + " format=NV12, framerate=21/1 ! nvvidconv flip-method="
#     + str(flip)
#     + " ! video/x-raw, width="
#     + str(w)
#     + ", height="
#     + str(h)
#     + ", format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
# )
# cam = cv2.VideoCapture(camSet)
# if not cam.isOpened():
#     print("Nie można otworzyć kamery!")
#     exit()

while True:

    if cv2.waitKey(1) == esc:
        break

    TrackbarPresets(state)

    new_img = LoadImageIfChanged(img_index_state)
    if new_img is not None:
        img = new_img
        height, width, _ = new_img.shape
        wod = (int)(width / 2 - 0.3 * width)
        wdo = (int)(width / 2 + 0.3 * width)
        hod = (int)(height / 2 - 0.25 * height)
        hdo = (int)(height / 2 + 0.38 * height)
        img = new_img[hod:hdo, wod:wdo]

    frame = cv2.resize(img, (w, h))
    window(frame, "frame = cv2.resize(img, (w, h))", 1, 0)

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

    # ret, frame = cam.read()
    # if not ret:
    #     continue
    # window(frame, mainWindowName, 0, 0)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # window(hsv, "hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)", 2, 0)

    FGMask = CreateFGMask(hsv)
    window(FGMask, 'FGMask = CreateFGMask(hsv)', 2, 0)

    HueMask = CreateFGMask(hsv)
    v_channel = hsv[:, :, 2]
    v_masked = cv2.bitwise_and(v_channel, v_channel, mask=HueMask)
    _, FGMask_HSV_Otsu = cv2.threshold(v_masked, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    window(FGMask_HSV_Otsu, 'FGMask = HSV + Otsu on V', 2, 2)

    FGMask = FGMask_HSV_Otsu

    FG = cv2.bitwise_and(frame, frame, mask=FGMask)
    window(FG, 'FG = cv2.bitwise_and(frame, frame, mask=FGMask)', 3, 0)

    BGMask = cv2.bitwise_not(FGMask)
    window(BGMask, 'BGMask = cv2.bitwise_not(FGMask)', 2, 1)

    # BG = cv2.bitwise_and(frame, img, mask=BGMask)
    # window(BG, 'BG = cv2.bitwise_and(frame, frame, mask=BGMask)', 3, 1)
    BG = cv2.cvtColor(BGMask, cv2.COLOR_GRAY2BGR)
    window(BG, 'BG = cv2.cvtColor(BGMask, cv2.COLOR_GRAY2BGR)', 3, 1)

    final = cv2.add(FG, BG)
    window(final, 'final = cv2.add(FG, BG)', 3, 2)

    # https://docs.opencv.org/4.1.1/d4/d73/tutorial_py_contours_begin.html
    contours, _ = cv2.findContours(FGMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # sort desc by area
    contours = sorted(contours, key=lambda x:cv2.contourArea(x), reverse=True)

    # draw on result frame
    # cv2.drawContours(frame, contours, 0, (255, 0, 0), 3)

    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area >= cv2.getTrackbarPos(tbnContourAreaThreshold, mainWindowName):
            x, y, ww, hh = cv2.boundingRect(contour)
            cv2.drawContours(frame, [contour], -1, blue, 3)
            cv2.rectangle(frame, (x, y), (x+ww, y+hh), red, 2)
            cv2.putText(frame, f"{i+1}", (((int)(x+ww/2), (int)(y+hh/2))), cv2.FONT_HERSHEY_SIMPLEX, 0.5, green, 2)

    cv2.rectangle(frame, ((int)(w/2) - 3, h - 15 - 3), ((int)(w/2) + 3, h - 15 + 3), green, 1)

    aim = (aimX, aimY) = (int)(w/2), h - 15
    min_distance = float("inf")
    distance_thresold = 10
    closest_center = None

    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour) 
        if area >= 50: 
            x, y, ww, hh = cv2.boundingRect(contour) 
            rect_center_x = int(x + ww / 2) 
            rect_center_y = int(y + hh / 2) 
            distance = math.hypot(aimX - rect_center_x, aimY - rect_center_y) 
            if distance < min_distance and distance > distance_thresold: 
                min_distance = distance 
                closest_center = (rect_center_x, rect_center_y)

    tolerance = 60
    if closest_center:
        dx = closest_center[0] - aimX
        nowStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        print(nowStr, aim, closest_center, dx, min_distance)
        if dx < -tolerance:
            print(nowStr, "left")
        elif dx > tolerance:
            print(nowStr, "right")
        else:
            print(nowStr, "ahead")
    else:
        print(nowStr, "stop")

    if closest_center: 
        cv2.line(frame, (aimX, aimY), closest_center, yellow, 1)
        # cv2.circle(frame, closest_center, 5, yellow, -1)
        # cv2.circle(frame, (aimX, aimY), 5, yellow, -1)

    window(frame, "frame", 1, 1)

# root.mainloop()

# cam.release()
cv2.destroyAllWindows()

# https://www.youtube.com/watch?v=zlIKoxaOo2M