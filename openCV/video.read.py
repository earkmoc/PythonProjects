import cv2

esc = 27
fps = 21
ms = int(1000 / fps)
video = cv2.VideoCapture("videos/myCam.avi")

while True:
    ret, frame = video.read()
    if not ret or cv2.waitKey(ms) == esc:
        break

    cv2.imshow("nanoCam", frame)
    cv2.moveWindow("nanoCam", 0, 0)

video.release()
cv2.destroyAllWindows()
