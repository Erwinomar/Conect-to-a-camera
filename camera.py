import cv2

# Jetson Nano (Linux) + Logitech C922 Pro USB webcam.
# V4L2 = the Linux video backend for USB cameras.
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # 0 = /dev/video0, the first camera

if not cap.isOpened():
    raise SystemExit(
        "Could not open camera. Check 'ls /dev/video*' and that nothing else is using it."
    )

# Ask for MJPG: the C922 streams raw YUYV by default, which caps you at ~5 fps
# at 720p. MJPG lets it do 720p/1080p at 30 fps.
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 30)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    cv2.imshow("Camera", frame)

    # quit on 'q' or if the window is closed
    if cv2.waitKey(1) == ord("q"):
        break
    if cv2.getWindowProperty("Camera", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
