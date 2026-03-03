# 👁️ Smart Drowsiness Detection & Gesture-Controlled Alert System

> **An integrated AI-IoT safety solution combining Computer Vision and Arduino to prevent driver fatigue-related accidents.**

## 📌 Problem Statement
Driver drowsiness causes thousands of road accidents every year. Most existing alert systems trigger false alarms or ignore user intent, and manual systems fail when a driver is fatigued. This project solves this by combining face authorization, eye-based drowsiness detection, and gesture-based control with physical hardware alerts.

## 🚀 Core Features
* **Biometric Authorization:** Uses facial recognition to detect and verify authorized drivers before activating the system.
* **Drowsiness Detection (EAR):** Tracks eye landmarks and calculates the Eye Aspect Ratio (EAR). Triggers an alert only if eyes remain closed for over 5 continuous seconds to prevent false positives from natural blinking.
* **Gesture-Controlled Alerts:** Utilizes hand landmark detection. A "fist" gesture activates a secondary blue LED alert without triggering the main buzzer.
* **Real-Time Hardware IoT:** Interfaces Python directly with an Arduino Uno to trigger physical LEDs and a buzzer instantly.

## 🛠 Tech Stack
* **Software:** Python 3.9, OpenCV, MediaPipe (Face Mesh & Hands), `face_recognition`, NumPy, PyFirmata.
* **Hardware:** Arduino Uno, Red LED (Pin 13), Blue LED (Pin 3), Piezo Buzzer (Pin 11).

## 📐 System Architecture
1. Webcam captures live video feed.
2. `face_recognition` verifies if the current driver is authorized.
3. MediaPipe extracts eye landmarks to calculate EAR and hand landmarks for gesture tracking.
4. Python logic processes thresholds (EAR < 0.25 for 5 seconds, or all fingertips folded inward for a fist).
5. PyFirmata sends precise activation signals via COM port to the Arduino Uno.

## 📂 Project Structure
* `captureAuthorizedUser.py`: Utility script to capture "open eye" and "closed eye" images of the authorized user.
* `DrowsinessDetection_GestureControl.py`: The main engine handling the video stream, AI inference, and Arduino communication.
* `authorized/`: Directory storing authorized user reference images.

## 💻 Installation & Setup

**Step 1. Install dependencies**
```bash
pip install opencv-python mediapipe face_recognition numpy pyfirmata

```

**Step 2. Hardware Preparation**

* Connect your Arduino Uno.
* Open the Arduino IDE, go to **File > Examples > Firmata > StandardFirmata**, and upload it to your board.
* Note the COM port your Arduino is connected to.

**Step 3. Capture authorized user**

```bash
python captureAuthorizedUser.py

```

*(Press 'o' to capture open eyes, 'c' for closed eyes)*

**Step 4. Run the main system**

```bash
python DrowsinessDetection_GestureControl.py

```

*(Enter your Arduino's COM port number when prompted in the terminal)*

## 💡 Output Behavior

* **Unauthorized face:** System remains inactive; no alerts.
* **Authorized face, normal state:** System monitors actively; no alerts.
* **Eyes closed > 5 seconds:** Red LED and Buzzer activate.
* **Fist gesture detected:** Blue LED activates.
