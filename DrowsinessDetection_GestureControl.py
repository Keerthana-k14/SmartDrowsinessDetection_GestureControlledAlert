import cv2
import numpy as np
import face_recognition
import mediapipe as mp
import pyfirmata
import time
import os


# ========== Arduino Setup ==========
port = input("Enter Arduino port number only (e.g., 3 for COM3): ")
com = "COM" + port
print(f"Connecting to {com}...")
board = pyfirmata.Arduino(com)
it = pyfirmata.util.Iterator(board)
it.start()

# LED and Buzzer Setup
red_led = board.digital[13]    # Red LED → Drowsiness Alert
blue_led = board.digital[3]   # Blue LED → Gesture
buzzer = board.digital[11]     # Buzzer
red_led.mode = pyfirmata.OUTPUT
blue_led.mode = pyfirmata.OUTPUT
buzzer.mode = pyfirmata.OUTPUT

# ========== Load Authorized Face ==========
def get_face_encoding(image_path):
    img = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(img)
    if encodings:
        return encodings[0]
    return None

if not os.path.exists("authorized/open.jpg"):
    print("⚠️ Authorized image not found. Please run capture_authorized_face.py first.")
    exit()

auth_encoding = get_face_encoding("authorized/open.jpg")
if auth_encoding is None:
    print("❌ Failed to encode authorized face.")
    exit()

# ========== Mediapipe Setup ==========
mp_face = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
face_mesh = mp_face.FaceMesh(refine_landmarks=True)
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [263, 387, 385, 362, 380, 373]

def eye_aspect_ratio(landmarks, eye_indices, w, h):
    eye = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in eye_indices]
    v1 = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
    v2 = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
    h_len = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))
    return (v1 + v2) / (2.0 * h_len)

# ========== Start Camera ==========
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open webcam.")
    board.exit()
    exit()

eye_closed_time = None
print("System running... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape

    # ========== Face Recognition ==========
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    authorized_present = False
    for encoding in face_encodings:
        match = face_recognition.compare_faces([auth_encoding], encoding, tolerance=0.5)
        if match[0]:
            authorized_present = True
            break

    # Initialize defaults
    eyes_closed = False
    fist_detected = False
    status = "Unauthorized or No Face"

    if authorized_present:
        # ======= Drowsiness Detection =======
        face_results = face_mesh.process(rgb_frame)
        if face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0].landmark
            left_ear = eye_aspect_ratio(landmarks, LEFT_EYE, w, h)
            right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)
            avg_ear = (left_ear + right_ear) / 2

            if avg_ear < 0.25:
                if eye_closed_time is None:
                    eye_closed_time = time.time()
                elif time.time() - eye_closed_time > 5:
                    eyes_closed = True
            else:
                eye_closed_time = None
        else:
            eye_closed_time = None

        # ======= Gesture Detection (Fist) =======
        hand_results = hands.process(rgb_frame)
        if hand_results.multi_hand_landmarks:
            hand_landmarks = hand_results.multi_hand_landmarks[0]
            tips = [8, 12, 16, 20]
            is_fist = all(
                hand_landmarks.landmark[tip].y > hand_landmarks.landmark[tip - 2].y
                for tip in tips
            )
            if is_fist:
                fist_detected = True

        # ======= Output Logic =======
        if eyes_closed:
            red_led.write(1)
            blue_led.write(0)
            buzzer.write(1)
            status = "Authorized: EYES CLOSED > 5s | ALERT!"
        elif fist_detected:
            red_led.write(0)
            blue_led.write(1)
            buzzer.write(0)
            status = "Authorized: FIST DETECTED | LED ON"
        else:
            red_led.write(0)
            blue_led.write(0)
            buzzer.write(0)
            status = "Authorized: Normal"

    else:
        # Unauthorized face or none
        red_led.write(0)
        blue_led.write(0)
        buzzer.write(0)

    # ======= Display =======
    cv2.putText(frame, status, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 0, 255) if "ALERT" in status else (0, 255, 0), 2)
    cv2.imshow("Smart Drowsiness + Gesture Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ========== Cleanup ==========
red_led.write(0)
blue_led.write(0)
buzzer.write(0)
cap.release()
cv2.destroyAllWindows()
board.exit()
