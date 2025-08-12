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
name4Window = "nanoCam"

while True:
    ret, frame = cam.read()

    if ret:
        roi = frame[50:250, 200:400]

        cv2.imshow("roi", roi)
        cv2.moveWindow("roi", 0, 535)

        roig = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cv2.imshow("roig", roig)
        cv2.moveWindow("roig", 270, 535)

        roig = cv2.cvtColor(roig, cv2.COLOR_GRAY2BGR)
        frame[50:250, 200:400] = roig
        cv2.imshow(name4Window, frame)
        cv2.moveWindow(name4Window, 0, 0)

    if cv2.waitKey(1) == esc:
        break

cam.release()
cv2.destroyAllWindows()
