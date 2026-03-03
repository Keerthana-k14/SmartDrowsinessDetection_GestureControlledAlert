import cv2
import os

# ========== Setup ==========
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera not accessible")
    exit()

print("Press 'o' to capture OPEN eyes image.")
print("Then press 'c' to capture CLOSED eyes image.")

open_image = None
closed_image = None


# ========== Capture Loop ==========
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    cv2.putText(frame, "Press 'o' for open eyes | 'c' for closed eyes | 'q' to quit",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.imshow("Capture Authorized Face", frame)

    key = cv2.waitKey(1)

    if key == ord('o'):
        open_image = frame.copy()
        print("✅ Open eyes image captured.")
    elif key == ord('c'):
        if open_image is not None:
            closed_image = frame.copy()
            print("✅ Closed eyes image captured.")
            break
        else:
            print("⚠️ Capture open eyes image first.")
    elif key == ord('q'):
        break

# ========== Save Images ==========
if open_image is not None and closed_image is not None:
    if not os.path.exists("authorized"):
        os.mkdir("authorized")
    cv2.imwrite("authorized/open.jpg", open_image)
    cv2.imwrite("authorized/closed.jpg", closed_image)
    print("✅ Authorized images saved in 'authorized/' folder.")
else:
    print("⚠️ Images not properly captured.")

cap.release()
cv2.destroyAllWindows()
