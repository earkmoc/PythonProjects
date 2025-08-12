import cv2


def click(event, x, y, flags, params):
    global point
    global mouseEvent
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, y, event, flags, params)
        point = (x, y)
        mouseEvent = event


dispW = 640
dispH = 480
flip = 0
esc = 27

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
cv2.setMouseCallback(name4Window, click)
mouseEvent = -1

while True:
    ret, frame = cam.read()
    retWeb, frameWeb = camWeb.read()

    if ret:
        if mouseEvent == 1:
            cv2.circle(frame, point, 15, (0, 255), -1)

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
