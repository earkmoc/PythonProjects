import cv2

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

while True:
    ret, frame = cam.read()
    retWeb, frameWeb = camWeb.read()

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
