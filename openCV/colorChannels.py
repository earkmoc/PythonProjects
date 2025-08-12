import cv2
import numpy as np

esc = 27
flip = 0

w = 640
h = 480


def window(img, name, c, r):
    cv2.imshow(name, img)
    cv2.moveWindow(name, 100 + c * w, 50 + r * (h + 28))


mainWindowName = 'nanoCam'

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

blank = np.zeros([h, w, 1], np.uint8)
# window(blank, 'blank', 2, 0)

while True:
    ret, frame = cam.read()

    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        print(frame.shape)
        print(frame.size)
        window(frame, mainWindowName, 0, 0)

        # b = cv2.split(frame)[0]
        # g = cv2.split(frame)[1]
        # r = cv2.split(frame)[2]
        b, g, r = cv2.split(frame)
        # b = cv2.cvtColor(b, cv2.COLOR_GRAY2BGR)

        # g[:] = g[:] * 2
        merge = cv2.merge((b, g, r))
        window(merge, 'merge', 2, 0)

        b = cv2.merge((b, blank, blank))
        g = cv2.merge((blank, g, blank))
        r = cv2.merge((blank, blank, r))

        window(b, 'b', 1, 0)
        window(g, 'g', 0, 1)
        window(r, 'r', 1, 1)

    if cv2.waitKey(1) == esc:
        break

cam.release()
cv2.destroyAllWindows()

# https://www.youtube.com/watch?v=55eYTGDAEjU