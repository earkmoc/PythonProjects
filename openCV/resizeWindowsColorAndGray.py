import cv2

dispW = 640
dispH = 480
flip = 0

camSet = (
    "nvarguscamerasrc !  video/x-raw(memory:NVMM), width=3264, height=2464, format=NV12, framerate=21/1 ! nvvidconv flip-method="
    + str(flip)
    + " ! video/x-raw, width="
    + str(dispW)
    + ", height="
    + str(dispH)
    + ", format=BGRx ! videoconvert ! video/x-raw, format=BGR ! appsink"
)
cam = cv2.VideoCapture(camSet)

while True:
    ret, frame = cam.read()

    cv2.imshow("nanoCam", frame)
    cv2.moveWindow("nanoCam", 0, 0)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow("grayVideo", gray)
    cv2.moveWindow("grayVideo", 0, 532)

    frameSmall = cv2.resize(frame, (320, 240))
    cv2.imshow("nanoCam small", frameSmall)
    cv2.moveWindow("nanoCam small", 705, 0)

    graySmall = cv2.resize(gray, (320, 240))
    cv2.imshow("gray small", graySmall)
    cv2.moveWindow("gray small", 705, 532)

    if cv2.waitKey(1) == ord("q"):
        break

cam.release()
cv2.destroyAllWindows()
