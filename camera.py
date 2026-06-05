import cv2

cap = cv2.VideoCapture(0)          # 0 = first camera

while True:
    ok, frame = cap.read()
    if not ok:
        break
    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) == ord("q"):  # press q to quit
        break

cap.release()
cv2.destroyAllWindows()
