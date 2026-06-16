import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Trying camera index {i}")
        ret, frame = cap.read()
        if ret:
            cv2.imshow(f"Camera {i}", frame)
            cv2.waitKey(1000)
            cv2.destroyAllWindows()
        cap.release()

video_capture = cv2.VideoCapture(0)  # try 1, 2, etc.
