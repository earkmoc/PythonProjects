import cv2
import numpy as np

esc = 27
flip = 0

W = 320
H = 240
green = (0, 255, 0)


def window(img, name, c, r):
    cv2.imshow(name, img)
    cv2.moveWindow(name, 100 + c * W, 50 + r * (H + 28))


def nothing():
    pass


mainWindowName = 'nanoCam'
cv2.namedWindow(mainWindowName)

trackbarNameHL = 'hueL'
cv2.createTrackbar(trackbarNameHL, mainWindowName, 162, 179, nothing)

trackbarNameHH = 'hueH'
cv2.createTrackbar(trackbarNameHH, mainWindowName, 0, 179, nothing)

trackbarNameSL = 'satL'
cv2.createTrackbar(trackbarNameSL, mainWindowName, 85, 255, nothing)

trackbarNameSH = 'satH'
cv2.createTrackbar(trackbarNameSH, mainWindowName, 255, 255, nothing)

trackbarNameVL = 'valL'
cv2.createTrackbar(trackbarNameVL, mainWindowName, 137, 255, nothing)

trackbarNameVH = 'valH'
cv2.createTrackbar(trackbarNameVH, mainWindowName, 255, 255, nothing)

camSet = (
    "nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464,"
    + " format=NV12, framerate=21/1 ! nvvidconv flip-method="
    + str(flip)
    + " ! video/x-raw, width="
    + str(W)
    + ", height="
    + str(H)
    + ", format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
)
cam = cv2.VideoCapture(camSet)

while True:
    if cv2.waitKey(1) == esc:
        break

    ret, frame = cam.read()
    if not ret:
        continue

    window(frame, mainWindowName, 0, 0)

    img = frame
    # img = cv2.resize(frame, (ww, hh))
    # window(img, "img = cv2.resize(img, (w, h))", 1, 0)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    hl = cv2.getTrackbarPos(trackbarNameHL, mainWindowName)
    hh = cv2.getTrackbarPos(trackbarNameHH, mainWindowName)
    sl = cv2.getTrackbarPos(trackbarNameSL, mainWindowName)
    sh = cv2.getTrackbarPos(trackbarNameSH, mainWindowName)
    vl = cv2.getTrackbarPos(trackbarNameVL, mainWindowName)
    vh = cv2.getTrackbarPos(trackbarNameVH, mainWindowName)

    if hl < hh:
        hsvl = np.array([hl, sl, vl])
        hsvh = np.array([hh, sh, vh])
        FGMask = cv2.inRange(hsv, hsvl, hsvh)
        window(FGMask, 'FGMask = cv2.inRange(hsv, hsvl, hsvh)', 1, 1)
    else:
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

        FGMask = cv2.add(FGMask1, FGMask2)
        window(FGMask, 'FGMask = cv2.add(FGMask1, FGMask2)', 1, 1)

    # https://docs.opencv.org/4.1.1/d4/d73/tutorial_py_contours_begin.html
    contours, _ = cv2.findContours(FGMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # sort desc by area
    contours = sorted(contours, key=lambda x:cv2.contourArea(x), reverse=True)

    # draw on result img
    # cv2.drawContours(img, contours, 0, (255, 0, 0), 3)

    for contour in contours:
        area = cv2.contourArea(contour)
        (x, y, w, h) = cv2.boundingRect(contour)
        if area >= 200:
            # draw on result img
            # cv2.drawContours(img, [cnt], -1, (255, 0, 0), 3)
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 3)
            img = cv2.line(img, (0, (int)(y+h/2)), (W, (int)(y+h/2)), green, 1)
            img = cv2.line(img, ((int)(x+w/2), 0), ((int)(x+w/2), H), green, 1)

    window(img, "img = cv2.resize(img, (W, H))", 2, 1)

cam.release()
cv2.destroyAllWindows()

# https://www.youtube.com/watch?v=lxFPM93Qe8o