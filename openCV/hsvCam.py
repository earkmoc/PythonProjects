import cv2
import numpy as np

esc = 27
flip = 0

w = 320
h = 240


def window(img, name, c, r):
    cv2.imshow(name, img)
    cv2.moveWindow(name, 100 + c * w, 50 + r * (h + 28))


def nothing():
    pass


mainWindowName = 'nanoCam'
cv2.namedWindow(mainWindowName)

trackbarNameHL = 'hueL'
cv2.createTrackbar(trackbarNameHL, mainWindowName, 166, 179, nothing)

trackbarNameHH = 'hueH'
cv2.createTrackbar(trackbarNameHH, mainWindowName, 0, 179, nothing)

trackbarNameSL = 'satL'
cv2.createTrackbar(trackbarNameSL, mainWindowName, 41, 255, nothing)

trackbarNameSH = 'satH'
cv2.createTrackbar(trackbarNameSH, mainWindowName, 255, 255, nothing)

trackbarNameVL = 'valL'
cv2.createTrackbar(trackbarNameVL, mainWindowName, 227, 255, nothing)

trackbarNameVH = 'valH'
cv2.createTrackbar(trackbarNameVH, mainWindowName, 255, 255, nothing)

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
cam = cv2.VideoCapture(camSet)

while True:
    ret, frame = cam.read()

    if ret:
        window(frame, mainWindowName, 0, 0)

        logo = frame
        logo = cv2.resize(logo, (w, h))
        window(logo, "logo=cv2.imread('pl.jpg')", 1, 0)

        hsv = cv2.cvtColor(logo, cv2.COLOR_BGR2HSV)
        # window(hsv, "hsv = cv2.cvtColor(logo, cv2.COLOR_BGR2HSV)", 2, 0)

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

        window(FGMask, 'FGMask = cv2.inRange(hsv, hsvl, hsvh)', 2, 0)

        FG = cv2.bitwise_and(logo, logo, mask=FGMask)
        window(FG, 'FG = cv2.bitwise_and(logo, logo, mask=FGMask)', 3, 0)

        BGMask = cv2.bitwise_not(FGMask)
        window(BGMask, 'BGMask = cv2.bitwise_not(FGMask)', 2, 1)

        # BG = cv2.bitwise_and(logo, logo, mask=BGMask)
        # window(BG, 'BG = cv2.bitwise_and(logo, logo, mask=BGMask)', 3, 1)
        BG = cv2.cvtColor(BGMask, cv2.COLOR_GRAY2BGR)
        window(BG, 'BG = cv2.cvtColor(BGMask, cv2.COLOR_GRAY2BGR)', 3, 1)

        final = cv2.add(FG, BG)
        window(final, 'final = cv2.add(FG, BG)', 3, 2)

    if cv2.waitKey(1) == esc:
        break

cam.release()
cv2.destroyAllWindows()

# https://www.youtube.com/watch?v=zlIKoxaOo2M