import cv2


def nothing(x):
    pass


esc = 27
flip = 0
dispW = 640
dispH = 480

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
camWeb = cv2.VideoCapture(1)

name4Window = "nanoCam"
cv2.namedWindow(name4Window)
cv2.createTrackbar("xVal", name4Window, 25, dispW, nothing)
cv2.createTrackbar("yVal", name4Window, 25, dispH, nothing)

while True:
    ret, frame = cam.read()
    retWeb, frameWeb = camWeb.read()

    xVal = cv2.getTrackbarPos("xVal", name4Window)
    yVal = cv2.getTrackbarPos("yVal", name4Window)
    cv2.circle(frame, (xVal, yVal), 5, (0, 0, 255), -1)

    if ret:
        cv2.imshow("nanoCam", frame)
        cv2.moveWindow("nanoCam", 0, 0)

    if retWeb:
        cv2.imshow("WebCam", frameWeb)
        cv2.moveWindow("WebCam", 0, 535)

    if cv2.waitKey(1) == esc:
        break

cam.release()
camWeb.release()
cv2.destroyAllWindows()
