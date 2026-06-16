import face_recognition
import cv2

image = face_recognition.load_image_file("authorized_face_resized.jpg")
print("Original shape:", image.shape)

# Resize and convert
small = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

encodings = face_recognition.face_encodings(rgb)
print(f"✅ Faces found: {len(encodings)}")
