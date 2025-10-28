import cv2
import face_recognition
import os
import numpy as np
import csv
import time
import logging
import psutil

# logging
logging.basicConfig(
    filename="performance.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Attendance File 
attendance_file = "attendance.csv"
if not os.path.exists(attendance_file):
    with open(attendance_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Time"])

dataset_path = "dataset"
known_encodings = []
known_names = []

for file in os.listdir(dataset_path):
    if file.endswith((".jpg", ".png", ".jpeg")):
        image = face_recognition.load_image_file(os.path.join(dataset_path, file))
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_encodings.append(encoding[0])
            known_names.append(os.path.splitext(file)[0])
            logging.info(f"Loaded encoding for {file}")

# last logged in 
last_logged = {}  
COOLDOWN = 60     

# Camera Initializarion
video = cv2.VideoCapture(0)

if not video.isOpened():
    logging.error("Camera could not be opened")
    exit()

logging.info("Camera opened successfully")

while True:
    start_time = time.time()
    ret, frame = video.read()
    if not ret:
        logging.warning("Frame not captured from camera")
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]

        if name != "Unknown":
            current_time = time.time()
            if name not in last_logged or (current_time - last_logged[name]) > COOLDOWN:
                with open(attendance_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([name, time.strftime("%Y-%m-%d %H:%M:%S")])
                last_logged[name] = current_time
                logging.info(f"Attendance marked for {name}")

        top, right, bottom, left = [v * 4 for v in face_location]
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    end_time = time.time()
    elapsed = end_time - start_time
    frame_time = elapsed * 1000
    fps = 1.0 / elapsed if elapsed > 0 else 0
    process = psutil.Process(os.getpid())
    cpu_usage = psutil.cpu_percent()
    memory_usage = process.memory_info().rss / (1024 * 1024)

    logging.info(f"Frame processed in {frame_time:.2f} ms (FPS: {fps:.2f}), CPU: {cpu_usage}%, Memory: {memory_usage:.2f} MB")

    cv2.imshow("Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video.release()
cv2.destroyAllWindows()
logging.info("Application closed")