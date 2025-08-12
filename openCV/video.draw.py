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
x = dispW - w - 40
y = dispH - h - 30
dx = 3
dy = 7

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

while True:
    ret, frame = cam.read()

    if ret:
        x += dx
        y += dy

        if 1 == 2:
            if x <= 0 or x >= dispW - w:
                dx = -dx
            if y <= 0 or y >= dispH - h:
                dy = -dy
            frame = cv2.rectangle(frame, (x, y), (x + w, y + h), red, -4)

        if 1 == 1:
            if x - r <= 0 or x >= dispW - r:
                dx = -dx
            if y - r <= 0 or y >= dispH - r:
                dy = -dy
            frame = cv2.circle(frame, (x, y), r, green, 2)

        # font = cv2.FONT_HERSHEY_DUPLEX
        # frame = cv2.putText(frame, "some text", (w, h), font, 1, red, 2)

        # frame = cv2.line(frame, (0, 0), (w, 0), green, 5)
        # frame = cv2.arrowedLine(frame, (10, 10), (w + 40, h + 40), blue, 5)

        # cv2.moveWindow("nanoCam", 0, 0)
        cv2.imshow("nanoCam", frame)

    if cv2.waitKey(1) == esc:
        break

cam.release()
cv2.destroyAllWindows()
