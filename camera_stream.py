"""
Headless camera viewer for the Jetson Nano over SSH.

Instead of cv2.imshow (which needs a local display), this serves the
camera as an MJPEG stream over HTTP. Run it on the Nano, then open
    http://<nano-ip>:8080
in a browser on your PC.

Stop with Ctrl+C.
"""

import cv2
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8080

cap = cv2.VideoCapture(0)  # 0 = /dev/video0, the C922
if not cap.isOpened():
    raise SystemExit(
        "Could not open camera. Check 'ls /dev/video*' and that nothing else is using it."
    )

# Tune for the C922 (best effort; ignored if the build lacks these helpers).
try:
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
except AttributeError:
    print("Note: skipping MJPG/resolution setup (not supported by this OpenCV build).")


class StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header(
            "Content-Type", "multipart/x-mixed-replace; boundary=frame"
        )
        self.end_headers()

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            ok, jpg = cv2.imencode(".jpg", frame)
            if not ok:
                continue
            try:
                self.wfile.write(b"--frame\r\n")
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Length", str(len(jpg)))
                self.end_headers()
                self.wfile.write(jpg.tobytes())
                self.wfile.write(b"\r\n")
            except (BrokenPipeError, ConnectionResetError):
                # Browser tab closed; stop this stream.
                break

    def log_message(self, *args):
        pass  # silence per-frame logging


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), StreamHandler)
    print(f"Streaming on http://<nano-ip>:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        server.server_close()
