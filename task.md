# Gesture Recognition Task

## Objective
Extend the current **Face Recognition Attendance System** by adding **Hand Gesture Detection** features.

The system should be able to:
1. Detect **if a hand is present** in the camera feed.
2. Identify **which hand it is** (Left Hand or Right Hand).
3. Count the **number of fingers** being shown.
4. Recognize **specific gestures** like:
   - 👍 Thumbs Up
   - 👎 Thumbs Down

---

## Inputs & Outputs

### Input
- **Live video frames** from the Camera (same input source as face recognition).
- Frames will contain **hands** with different poses and gestures.

### Output
- **Hand Presence**: "Hand Detected" or "No Hand".
- **Hand Side**: "Left Hand" or "Right Hand".
- **Finger Count**: Number of fingers shown (0–5).
- **Gesture Type**: "Thumbs Up", "Thumbs Down", or "Other".

---

## Tasks Breakdown

### 1. Hand Detection
- Use a library like **OpenCV** or **MediaPipe Hands**.
- Detect bounding boxes around hands in each frame.
- Output: `Hand Detected` + bounding box coordinates.

### 2. Hand Side Identification (Left / Right)
- From detected hand landmarks, decide if it is the **left hand** or **right hand**.
- Output: `"Left Hand"` or `"Right Hand"`.

### 3. Finger Counting
- Based on hand landmarks:
  - Check which fingers are **open** or **closed**.
  - Count the total number of open fingers.
- Output: `"Finger Count: N"`.

### 4. Gesture Recognition
- Define rules for common gestures:
  - **Thumbs Up**: Thumb extended, all other fingers folded.
  - **Thumbs Down**: Thumb down, all other fingers folded.
- Output: `"Gesture: Thumbs Up"` or `"Gesture: Thumbs Down"`.

---

## Storage & Logging

- Extend the **Logger** module to also record:
  - Gesture detection events.
  - Performance details (CPU, memory usage).
    AttendanceManager --> CSV
    AttendanceManager --> Logger
    Logger --> LogFile
