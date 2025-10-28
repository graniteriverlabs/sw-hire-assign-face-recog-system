"""
Hand Gesture Recognition using ONLY SmolVLM
No MediaPipe fallback - pure SmolVLM vision-language model
"""

import cv2
import time
import psutil
import logging
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForVision2Seq

# Try to load SmolVLM model - REQUIRED, no fallback
print("Loading SmolVLM model...")
print("This is required for this application. Make sure transformers and torch are installed.")

SMOLVLM_AVAILABLE = False
model = None
processor = None

try:
    print("Attempting to load model from HuggingFaceTB/SmolVLM-Instruct...")
    print("This may take a few minutes on first run as the model downloads (~1.5GB)...")
    model_name = "HuggingFaceTB/SmolVLM-Instruct"
    
    print("Loading processor...")
    processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    print("Processor loaded successfully!")
    
    print("Loading model weights...")
    if torch.cuda.is_available():
        print(f"✓ CUDA available! Using GPU: {torch.cuda.get_device_name(0)}")
        model = AutoModelForVision2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
    else:
        print("⚠️  CUDA not available, using CPU (this will be slower)")
        model = AutoModelForVision2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            trust_remote_code=True
        )
        model = model.to("cpu")
    
    SMOLVLM_AVAILABLE = True
    print("✓ SmolVLM model loaded successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nPlease install required packages:")
    print("  pip install transformers torch accelerate")
    import sys
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error loading SmolVLM model: {e}")
    print("\nModel loading failed. This application requires SmolVLM to run.")
    print("\nTroubleshooting:")
    print("1. Make sure you have internet connection (first time download)")
    print("2. Check if you have enough disk space (~1.5GB)")
    print("3. Verify installation: pip install transformers torch")
    import sys
    sys.exit(1)


def setup_logging():
    """Setup logging to file with timestamp"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"gesture_recognition_smolvlm_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def query_smolvlm(frame, prompt: str) -> str:
    """Query SmolVLM with a prompt about the image"""
    if not SMOLVLM_AVAILABLE or model is None or processor is None:
        return None
    
    try:
        # Convert frame to PIL Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        
        # SmolVLM expects messages in a specific format
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image"},
                    {"type": "text", "text": prompt}
                ]
            },
        ]
        
        # Apply chat template
        text_prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
        
        # Process image and text
        inputs = processor(text=text_prompt, images=[pil_image], return_tensors="pt")
        
        # Move inputs to same device as model
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=150)
        
        # Decode the output (remove the prompt part to get just the response)
        generated_text = processor.batch_decode(
            outputs, 
            skip_special_tokens=True
        )[0]
        
        # Extract just the AI response (remove the prompt)
        if text_prompt in generated_text:
            response = generated_text.split(text_prompt)[-1].strip()
        else:
            response = generated_text
        
        return response
        
    except Exception as e:
        print(f"Error querying SmolVLM: {e}")
        import traceback
        traceback.print_exc()
        return None


def extract_gesture_info(smolvlm_response: str) -> dict:
    """
    Parse SmolVLM response to extract gesture information
    Returns dict with hand_side, fingers_count, and gesture
    """
    response_lower = smolvlm_response.lower()
    
    result = {
        'hand_side': None,
        'fingers_count': None,
        'gesture': None,
        'raw_response': smolvlm_response
    }
    
    import re
    
    # Try to extract structured format first (Hand: Left, Fingers: 5, Gesture: thumbs_up)
    hand_match = re.search(r'hand:\s*([A-Za-z]+)', response_lower)
    fingers_match = re.search(r'fingers:\s*(\d+)', response_lower)
    gesture_match = re.search(r'gesture:\s*([A-Za-z_]+)', response_lower)
    
    if hand_match:
        hand = hand_match.group(1).strip()
        result['hand_side'] = 'Left' if 'left' in hand else 'Right' if 'right' in hand else None
    
    if fingers_match:
        try:
            result['fingers_count'] = int(fingers_match.group(1))
        except:
            pass
    
    if gesture_match:
        result['gesture'] = gesture_match.group(1).strip()
    
    # Fallback: Extract hand side
    if not result['hand_side']:
        if 'left hand' in response_lower or ('left' in response_lower and 'hand' in response_lower):
            result['hand_side'] = 'Left'
        elif 'right hand' in response_lower or ('right' in response_lower and 'hand' in response_lower):
            result['hand_side'] = 'Right'
    
    # Fallback: Extract gesture
    if not result['gesture']:
        if 'thumbs up' in response_lower or 'thumb up' in response_lower:
            result['gesture'] = 'thumbs_up'
        elif 'thumbs down' in response_lower or 'thumb down' in response_lower:
            result['gesture'] = 'thumbs_down'
        elif 'peace' in response_lower or 'victory' in response_lower:
            result['gesture'] = 'peace'
        elif 'ok' in response_lower or 'okay' in response_lower:
            result['gesture'] = 'ok'
        elif 'fist' in response_lower:
            result['gesture'] = 'fist'
        elif 'open' in response_lower and 'hand' in response_lower:
            result['gesture'] = 'open_hand'
    
    # Fallback: Extract finger count
    if result['fingers_count'] is None:
        finger_keywords = [
            'five fingers', 'four fingers', 'three fingers', 'two fingers', 'one finger',
            '5 fingers', '4 fingers', '3 fingers', '2 fingers', '1 finger'
        ]
        
        for keyword in finger_keywords:
            if keyword in response_lower:
                num = keyword.split()[0]
                try:
                    result['fingers_count'] = int(num)
                    break
                except:
                    # Handle word numbers
                    if 'five' in keyword or '5' in keyword:
                        result['fingers_count'] = 5
                    elif 'four' in keyword or '4' in keyword:
                        result['fingers_count'] = 4
                    elif 'three' in keyword or '3' in keyword:
                        result['fingers_count'] = 3
                    elif 'two' in keyword or '2' in keyword:
                        result['fingers_count'] = 2
                    elif 'one' in keyword or '1' in keyword:
                        result['fingers_count'] = 1
    
    return result


def process_frame_with_smolvlm(frame, logger) -> dict:
    """Process a single frame using SmolVLM exclusively"""
    
    # Create detailed prompt for gesture recognition
    prompt = (
        "Analyze this hand image. Answer in this exact format: "
        "Hand: [Left/Right], Fingers: [0-5], Gesture: [thumbs_up/thumbs_down/fist/open/ok/peace/none]. "
        "Describe what you see."
    )
    
    # Query SmolVLM
    smolvlm_response = query_smolvlm(frame, prompt)
    
    detection = {
        'hands_detected': 0,
        'hand_side': None,
        'fingers_count': None,
        'gesture': None,
        'smolvlm_response': smolvlm_response,
        'timestamp': time.time()
    }
    
    if smolvlm_response:
        # Parse the response
        info = extract_gesture_info(smolvlm_response)
        detection['hand_side'] = info['hand_side']
        detection['fingers_count'] = info['fingers_count']
        detection['gesture'] = info['gesture']
        detection['raw_smolvlm'] = info['raw_response']
        
        # Mark as hand detected if we got any response
        if info['hand_side'] or info['fingers_count'] is not None or info['gesture']:
            detection['hands_detected'] = 1
    
    # Add text annotations to frame
    y_offset = 30
    cv2.putText(frame, "SmolVLM Only Mode", (10, y_offset), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    y_offset += 35
    
    if detection['hand_side']:
        cv2.putText(frame, f"Hand: {detection['hand_side']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y_offset += 30
    
    if detection['fingers_count'] is not None:
        cv2.putText(frame, f"Fingers: {detection['fingers_count']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y_offset += 30
    
    if detection['gesture']:
        cv2.putText(frame, f"Gesture: {detection['gesture']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        y_offset += 30
    
    # Show raw SmolVLM response (last 100 chars to fit on screen)
    if detection['smolvlm_response']:
        display_response = detection['smolvlm_response'][:80] + "..." if len(detection['smolvlm_response']) > 80 else detection['smolvlm_response']
        cv2.putText(frame, f"AI: {display_response}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return detection


def get_system_metrics() -> dict:
    """Get CPU and memory usage"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=None),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_used_mb': psutil.virtual_memory().used / (1024 * 1024)
    }


def main():
    """Main function to run SmolVLM-only gesture recognition"""
    global frame_count
    frame_count = 0
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("Starting SmolVLM-Only Hand Gesture Recognition System")
    logger.info("No MediaPipe fallback - using SmolVLM exclusively")
    logger.info(f"Model device: {next(model.parameters()).device}")
    logger.info("=" * 60)
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("Failed to open camera")
        return
    
    frame_interval = 1.0  # 1 FPS
    last_frame_time = 0
    fps_history = []
    
    logger.info("Camera initialized. Processing at 1 FPS. Press 'q' to quit")
    
    try:
        while True:
            current_time = time.time()
            
            # Process frame only every second (1 FPS)
            if current_time - last_frame_time >= frame_interval:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame")
                    continue
                
                processing_start = time.time()
                
                # Process with SmolVLM only
                detection = process_frame_with_smolvlm(frame, logger)
                frame_count += 1
                
                processing_time = time.time() - processing_start
                actual_fps = 1.0 / processing_time if processing_time > 0 else 0
                fps_history.append(actual_fps)
                
                metrics = get_system_metrics()
                
                # Log comprehensive results
                log_message = (f"Frame {frame_count} | "
                             f"Hand: {detection['hand_side'] or 'None'} | "
                             f"Fingers: {detection['fingers_count'] or 'None'} | "
                             f"Gesture: {detection['gesture'] or 'None'} | "
                             f"FPS: {actual_fps:.2f} | "
                             f"CPU: {metrics['cpu_percent']:.1f}% | "
                             f"Memory: {metrics['memory_used_mb']:.1f} MB")
                
                if detection['smolvlm_response']:
                    log_message += f" | Response: {detection['smolvlm_response'][:100]}"
                
                logger.info(log_message)
                
                cv2.imshow('Hand Gesture Recognition - SmolVLM Only', frame)
                last_frame_time = current_time
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logger.info("Quitting application")
                break
            
            time.sleep(0.01)
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        avg_fps = np.mean(fps_history) if fps_history else 0
        logger.info("=" * 60)
        logger.info(f"Session complete. Total frames: {frame_count}, Avg FPS: {avg_fps:.2f}")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()

