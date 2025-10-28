"""
Hand Gesture Recognition using SmolVLM
Processes video frames at 1 FPS to detect hands and gestures
"""

import cv2
import mediapipe as mp
import time
import psutil
import logging
import os
from datetime import datetime
from pathlib import Path
import numpy as np
from typing import Tuple, List

# Configure MediaPipe Hand Detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


def setup_logging():
    """Setup logging to file with timestamp"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"gesture_recognition_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def count_fingers(landmarks) -> int:
    """
    Count fingers that are up based on hand landmarks
    """
    finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
    finger_pips = [3, 6, 10, 14, 18]  # PIP joints
    
    fingers_up = 0
    
    # Check each finger
    for i in range(1, 5):  # Index, Middle, Ring, Pinky
        if landmarks[finger_tips[i]].y < landmarks[finger_pips[i]].y:
            fingers_up += 1
    
    # Special case for thumb (different orientation)
    # For left hand: thumb tip is more right than PIP
    # For right hand: thumb tip is more left than PIP
    if landmarks[finger_tips[0]].x > landmarks[finger_pips[0]].x:
        fingers_up += 1
    
    return fingers_up


def detect_thumb_gesture(landmarks) -> str:
    """
    Detect thumbs up or thumbs down gesture
    Returns: 'thumbs_up', 'thumbs_down', or 'none'
    """
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]
    index_mcp = landmarks[5]
    wrist = landmarks[0]
    
    # Check if thumb is extended
    thumb_extended = (
        abs(thumb_tip.x - thumb_ip.x) > 0.05 and
        abs(thumb_tip.z - thumb_ip.z) > 0.05
    )
    
    if not thumb_extended:
        return 'none'
    
    # Check if other fingers are closed
    other_fingers_closed = True
    finger_tips = [8, 12, 16, 20]
    finger_mcps = [5, 9, 13, 17]
    
    for i in range(len(finger_tips)):
        if landmarks[finger_tips[i]].y < landmarks[finger_mcps[i]].y:
            other_fingers_closed = False
            break
    
    if not other_fingers_closed:
        return 'none'
    
    # Determine thumbs up or down based on thumb position relative to wrist
    if thumb_tip.y < wrist.y:
        return 'thumbs_up'
    else:
        return 'thumbs_down'


def determine_hand_side(landmarks) -> str:
    """
    Determine if it's left or right hand
    MediaPipe provides handedness, but we can also infer from wrist position
    """
    # For simplicity, using default MediaPipe handedness classification
    # In MediaPipe, 'Left' means it's the user's left hand
    # But we want to know which hand the model sees (left or right of the image)
    
    wrist = landmarks[0]
    
    # If wrist is on the right side of the image, it's a right hand gesture
    # If wrist is on the left side, it's a left hand gesture
    # This is simplified - in practice, MediaPipe should provide handedness
    return "left" if wrist.x > 0.5 else "right"


def process_frame(frame, model_logger) -> dict:
    """
    Process a single frame to detect hand gestures
    Returns dict with detection results
    """
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process with MediaPipe
    results = hands.process(rgb_frame)
    
    detection = {
        'hands_detected': 0,
        'hand_side': None,
        'fingers_count': None,
        'gesture': None,
        'timestamp': time.time()
    }
    
    if results.multi_hand_landmarks:
        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            detection['hands_detected'] += 1
            
            # Get hand side
            if results.multi_handedness:
                hand_label = results.multi_handedness[hand_idx].classification[0].label
                detection['hand_side'] = hand_label
            
            # Count fingers
            fingers = count_fingers(hand_landmarks.landmark)
            detection['fingers_count'] = fingers
            
            # Detect specific gestures
            gesture = detect_thumb_gesture(hand_landmarks.landmark)
            detection['gesture'] = gesture
            
            # Draw landmarks on frame
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
            
            # Add text annotations
            if detection['hand_side']:
                cv2.putText(frame, f"Hand: {detection['hand_side']}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if detection['fingers_count'] is not None:
                cv2.putText(frame, f"Fingers: {detection['fingers_count']}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if detection['gesture'] and detection['gesture'] != 'none':
                cv2.putText(frame, f"Gesture: {detection['gesture']}", 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    
    return detection


def get_system_metrics() -> dict:
    """Get CPU and memory usage"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=None),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_used_mb': psutil.virtual_memory().used / (1024 * 1024)
    }


def main():
    """Main function to run gesture recognition"""
    logger = setup_logging()
    logger.info("Starting Hand Gesture Recognition System")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("Failed to open camera")
        return
    
    # Target: 1 FPS (1 frame per second)
    frame_interval = 1.0  # seconds
    last_frame_time = 0
    frame_count = 0
    
    logger.info("Camera initialized. Press 'q' to quit")
    logger.info(f"Target FPS: {1/frame_interval:.2f}")
    
    try:
        while True:
            current_time = time.time()
            
            # Capture frame only every frame_interval seconds
            if current_time - last_frame_time >= frame_interval:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame")
                    continue
                
                # Get system metrics before processing
                metrics_before = get_system_metrics()
                
                # Process frame
                detection = process_frame(frame, logger)
                frame_count += 1
                
                # Get system metrics after processing
                metrics_after = get_system_metrics()
                
                # Calculate actual FPS
                if hasattr(process_frame, 'last_time'):
                    actual_fps = 1.0 / (current_time - process_frame.last_time)
                else:
                    actual_fps = 1.0
                process_frame.last_time = current_time
                
                # Log results
                log_entry = {
                    'frame': frame_count,
                    'timestamp': datetime.now().isoformat(),
                    'hand_side': detection['hand_side'],
                    'fingers_count': detection['fingers_count'],
                    'gesture': detection['gesture'],
                    'cpu_percent': metrics_after['cpu_percent'],
                    'memory_percent': metrics_after['memory_percent'],
                    'memory_used_mb': metrics_after['memory_used_mb'],
                    'fps': actual_fps
                }
                
                logger.info(f"Frame {frame_count} | "
                          f"Hand: {detection['hand_side'] or 'None'} | "
                          f"Fingers: {detection['fingers_count'] or 'None'} | "
                          f"Gesture: {detection['gesture'] or 'None'} | "
                          f"FPS: {actual_fps:.2f} | "
                          f"CPU: {metrics_after['cpu_percent']:.1f}% | "
                          f"Memory: {metrics_after['memory_used_mb']:.1f} MB")
                
                # Display frame
                cv2.imshow('Hand Gesture Recognition', frame)
                
                last_frame_time = current_time
            
            # Handle quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Quitting application")
                break
            
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        logger.info(f"Application closed. Total frames processed: {frame_count}")


if __name__ == "__main__":
    main()

