import cv2

esc = 27
flip = 0

dispW = 320
dispH = 240


def window(img, name, c, r):
    cv2.imshow(name, img)
    cv2.moveWindow(name, 100 + c * dispW, 50 + r * (dispH + 28))


def nothing():
    pass


trackBarName = 'BlendValue'
blendedWindowName = 'blended=addWeighted(frame, .5, cvLogo, .5, 0)'
cv2.namedWindow(blendedWindowName)
cv2.createTrackbar(trackBarName, blendedWindowName, 50, 100, nothing)

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
name4Window = "nanoCam"

cvLogo = cv2.imread('cv.jpg')
cvLogo = cv2.resize(cvLogo, (320, 240))
window(cvLogo, "cvLogo=cv2.imread('cv.jpg')", 1, 0)
window(cvLogo, "cvLogo=cv2.imread('cv.jpg') ", 0, 3)

cvLogoGray = cv2.cvtColor(cvLogo, cv2.COLOR_BGR2GRAY)
window(cvLogoGray, 'cvLogoGray=cvtColor(cvLogo, cv2.COLOR_BGR2GRAY)', 1, 1)

_, BGMask = cv2.threshold(cvLogoGray, 155, 255, cv2.THRESH_BINARY)
window(BGMask, 'BGMask=cv2.threshold(cvLogoGray, 225, 255, cv2.THRESH_BINARY)', 1, 2)

FGMask = cv2.bitwise_not(BGMask)
window(FGMask, 'FGMask=cv2.bitwise_not(BGMask)', 1, 3)

FG = cv2.bitwise_and(cvLogo, cvLogo, mask=FGMask)
window(FG, 'FG=cv2.bitwise_and(cvLogo, cvLogo, mask=FGMask)', 2, 3)

while True:
    ret, frame = cam.read()

    if ret:
        window(frame, name4Window, 0, 2)

        BG = cv2.bitwise_and(frame, frame, mask=BGMask)
        window(BG, 'BG=cv2.bitwise_and(frame, frame, mask=BGMask)', 2, 2)

        compImage = cv2.add(BG, FG)
        window(compImage, 'compImage=cv2.add(BG, FG)', 2, 4)

        # compImageOr = cv2.bitwise_or(BG, FG)
        # window(compImageOr, 'compImage=cv2.bitwise_or(BG, FG)', 3, 4)

        BV = cv2.getTrackbarPos(trackBarName, blendedWindowName)
        blended = cv2.addWeighted(frame, 1 - BV * 0.01, cvLogo, BV * 0.01, 0)
        window(blended, blendedWindowName, 3, 4)

        blendedFGMask = cv2.bitwise_and(blended, blended, mask=FGMask)
        window(blendedFGMask, 'blendedFGMask=bitwise_and(blended, blended, mask=FGMask)', 4, 4)

        compFinal = cv2.add(BG, blendedFGMask)
        window(compFinal, 'add(BG, blendedFGMask)', 5, 4)

    if cv2.waitKey(1) == esc:
        break

cam.release()
cv2.destroyAllWindows()

# https://www.youtube.com/watch?v=HkPnjDlz7NA 47:22