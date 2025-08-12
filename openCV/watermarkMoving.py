import cv2

esc = 27

red = (0, 0, 255)
green = (0, 255, 0)
blue = (255, 0, 0)

flip = 0
dispW = 640
dispH = 480

w = 100
h = 100
r = 50
# x = dispW - w - 40
# y = dispH - h - 30
x = 0
y = 0
dx = 3
dy = 7


def window(img, name, c, r):
    cv2.imshow(name, img)
    cv2.moveWindow(name, 100 + c * w, 50 + r * (h + 28))


def nothing():
    pass


mainWindowName = 'nanoCam'
trackBarName = 'TrackBar'
cv2.namedWindow(mainWindowName)
cv2.createTrackbar(trackBarName, mainWindowName, 217, 255, nothing)

camSet = (
    "nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464,"
    + " format=NV12, framerate=21/1 ! nvvidconv flip-method="
    + str(flip)
    + " ! video/x-raw, width="
    + str(dispW)
    + ", height="
    + str(dispH)
    + ", format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
)
cam = cv2.VideoCapture(camSet)

logo = cv2.imread('pl.jpg')
logo = cv2.resize(logo, (w, h))
window(logo, "logo=cv2.imread('pl.jpg')", 0, 0)

logoGray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
window(logoGray, 'logoGray=cvtColor(logo, cv2.COLOR_BGR2GRAY)', 0, 1)

while True:
    tbv = cv2.getTrackbarPos(trackBarName, mainWindowName)
    _, BGMask = cv2.threshold(logoGray, tbv, 255, cv2.THRESH_BINARY)
    window(BGMask, 'BGMask=cv2.threshold(logoGray, tbv, 255, cv2.THRESH_BINARY)', 0, 2)

    FGMask = cv2.bitwise_not(BGMask)
    window(FGMask, 'FGMask=cv2.bitwise_not(BGMask)', 0, 3)

    ret, frame = cam.read()

    if ret:
        x += dx
        y += dy

        if x <= 0 or x >= dispW - w - 2:
            dx = -dx
        if y <= 0 or y >= dispH - h - 2:
            dy = -dy

        roi = cv2.bitwise_and(logo, logo, mask=FGMask)
        window(roi, 'roi = cv2.bitwise_and(logo, logo, mask=FGMask)', 0, 4)

        oryg = frame[y:y+h, x:x+w]
        oryg = cv2.bitwise_and(oryg, oryg, mask=BGMask)
        window(oryg, 'oryg = cv2.bitwise_and(oryg, oryg, mask=BGMask)', 0, 5)

        oryg = cv2.add(oryg, roi)
        window(oryg, 'oryg = cv2.add(oryg, roi)', 0, 6)

        frame[y:y+h, x:x+w] = oryg
        window(frame, mainWindowName, 1, 0)

    if cv2.waitKey(1) == esc:
        break

cam.release()
cv2.destroyAllWindows()

# https://www.youtube.com/watch?v=BoofOszCTOE