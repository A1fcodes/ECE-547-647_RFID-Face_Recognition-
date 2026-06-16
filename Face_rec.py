import cv2
import face_recognition
import serial
import time
import os

# --- Setup Serial Connection ---
try:
    arduino = serial.Serial('/dev/tty.usbmodem101', 9600)
    time.sleep(2)  # Allow Arduino to reset
    print("✅ Serial port opened successfully")
except serial.SerialException as e:
    print(f"❌ Could not open serial port: {e}")
    exit()

# --- Load and Encode Multiple Known Faces ---
known_face_encodings = []
known_face_names = []

face_folder = "known_faces"

for filename in os.listdir(face_folder):
    if filename.endswith((".jpg", ".png")):
        name = os.path.splitext(filename)[0]
        path = os.path.join(face_folder, filename)
        image = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_face_encodings.append(encoding[0])
            known_face_names.append(name)
            print(f"✅ Loaded and encoded: {name}")
        else:
            print(f"⚠️ No face found in {filename}")

if not known_face_encodings:
    print("❌ No valid faces loaded.")
    arduino.close()
    exit()

# --- Start Webcam ---
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("❌ Failed to access webcam.")
    arduino.close()
    exit()

print("🎥 Webcam started. Press 'q' to quit.")

# --- Main Loop ---
try:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("❌ Failed to capture frame.")
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            if True in matches:
                name = known_face_names[matches.index(True)]
                print(f"✅ Recognized {name} — Sending to Arduino")
                arduino.write(b'face_ok\n')
                print("✅ Sent 'face_ok' to Arduino. Waiting for RFID...")

                start_time = time.time()
                timeout = 10  # seconds

                while True:
                    if arduino.in_waiting > 0:
                        response = arduino.readline().decode().strip()
                        print(f"📬 Arduino says: {response}")
                        if response == "rfid_ok":
                            print("✅ RFID verified. Exiting...")
                            raise SystemExit  # Trigger final cleanup
                    if time.time() - start_time > timeout:
                        print("⏳ Timeout waiting for RFID. Continuing scan...")
                        break
            else:
                print("⚠️ Face detected, but not recognized.")

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 Exiting...")
            break

except KeyboardInterrupt:
    print("🛑 Interrupted by user.")

# --- Cleanup ---
print("🧹 Cleaning up resources...")
video_capture.release()
cv2.destroyAllWindows()
arduino.close()
print("✅ Program ended cleanly.")
