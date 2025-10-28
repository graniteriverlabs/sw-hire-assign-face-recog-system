🎥 Face Recognition Attendance System

This project is a real-time face recognition–based attendance system that automatically marks attendance by detecting and recognizing faces using a webcam. It uses the face_recognition and OpenCV libraries to identify known individuals and logs their attendance with timestamps in a CSV file.

📋 Features

✅ Real-time face detection and recognition using webcam
✅ Automatic attendance marking with timestamp
✅ Performance logging (CPU usage, FPS, memory)
✅ Cooldown timer to prevent duplicate entries
✅ Easy to extend with more faces in the dataset

🧠 How It Works

The system loads all known faces from the dataset/ folder.

It computes facial encodings for each image and stores them in memory.

The webcam captures frames in real time.

Detected faces are compared against the known encodings.

If a match is found:

The person’s name and time are logged in attendance.csv.

The face is highlighted in the video feed.

System performance (FPS, CPU, Memory) is logged in performance.log.

🗂️ Project Structure
face-recognition-attendance/
│
├── dataset/                # Folder containing known face images (.jpg/.png)
│   ├── Alice.jpg
│   ├── Bob.jpg
│   └── ...
│
├── attendance.csv          # Automatically generated attendance log
├── performance.log         # Performance log file
├── main.py                 # Main program (the code you provided)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation

⚙️ Installation

Clone the repository

git clone https://github.com/yourusername/face-recognition-attendance.git
cd face-recognition-attendance


Create a virtual environment (optional but recommended)

python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows


Install dependencies

pip install -r requirements.txt


Add known faces

Place clear, front-facing photos of known individuals inside the dataset/ folder.

Name each image as the person’s name, e.g., John.jpg.

🚀 Usage

Run the program:

python main.py


A webcam window will open.

Detected faces will be recognized and logged in attendance.csv.

Press Q to quit the application.

🧩 Dependencies

OpenCV

face_recognition

dlib

NumPy

psutil

Install them using:

pip install -r requirements.txt

🧾 Logging

performance.log records frame processing time, FPS, CPU %, and memory usage.

Example log entry:

2025-10-28 10:23:45 - INFO - Frame processed in 33.21 ms (FPS: 29.98), CPU: 12.5%, Memory: 110.4 MB

🛡️ Notes

Make sure your webcam is properly connected.

Use high-quality, well-lit images in the dataset for better recognition accuracy.

Avoid very large image files — 300x300 to 500x500 pixels is ideal.

The default cooldown between two attendance logs for the same person is 60 seconds.
