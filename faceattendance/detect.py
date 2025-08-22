import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import pickle
from datetime import datetime

MODEL_PATH = 'models/cnn_face_model.h5'
ENCODER_PATH = 'models/label_encoder.pkl'
IMG_SIZE = (160, 160)
THRESHOLD = 0.6

# Load model and encoder
model = load_model(MODEL_PATH)
with open(ENCODER_PATH, 'rb') as f:
    le = pickle.load(f)

def mark_attendance(name):
    with open('attendance.csv', 'a') as f:
        now = datetime.now()
        f.write(f"{name},{now.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"Attendance marked for {name}")

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face_img = frame[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, IMG_SIZE)
        face_array = np.expand_dims(face_img / 255.0, axis=0)

        preds = model.predict(face_array)[0]
        max_idx = np.argmax(preds)
        confidence = preds[max_idx]
        name = le.inverse_transform([max_idx])[0] if confidence > THRESHOLD else "Unknown"

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f"{name} ({confidence:.2f})", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        if name != "Unknown":
            mark_attendance(name)

    cv2.imshow("CNN Attendance System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
