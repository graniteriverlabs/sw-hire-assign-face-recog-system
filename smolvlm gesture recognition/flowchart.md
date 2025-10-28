# Execution Flowchart

This document shows the execution flowchart for the gesture recognition system.

## Main Execution Flow

```mermaid
flowchart TD
    START([Start Application]) --> LOAD_CONFIG[Load config.json]
    LOAD_CONFIG --> READ_MODE[Read mode and approach]
    
    READ_MODE --> CHECK_MODE{mode?}
    
    CHECK_MODE -->|static| STATIC_PATH[Static Mode]
    CHECK_MODE -->|dynamic| DYNAMIC_PATH[Dynamic Mode]
    
    STATIC_PATH --> CHECK_APPROACH_STATIC{approach?}
    CHECK_APPROACH_STATIC -->|mediapipe| LOAD_MP[Load gesture_recognition.py]
    CHECK_APPROACH_STATIC -->|smolvlm| LOAD_SMOL[Load gesture_recognition_smolvlm_only.py]
    
    DYNAMIC_PATH --> INIT_MONITOR[Initialize Performance Monitor]
    INIT_MONITOR --> GET_START_APP[Get starting approach]
    GET_START_APP --> CHECK_APPROACH_DYNAMIC{starting approach?}
    CHECK_APPROACH_DYNAMIC -->|mediapipe| LOAD_MP_DYNAMIC[Load MediaPipe Module]
    CHECK_APPROACH_DYNAMIC -->|smolvlm| LOAD_SMOL_DYNAMIC[Load SmolVLM Module]
    
    LOAD_MP --> INIT_CAMERA_MP[Initialize Camera<br/>camera_index: 0]
    LOAD_SMOL --> INIT_CAMERA_SMOL[Initialize Camera<br/>camera_index: 0]
    LOAD_MP_DYNAMIC --> INIT_CAMERA_DYNAMIC[Initialize Camera<br/>camera_index: 0]
    LOAD_SMOL_DYNAMIC --> INIT_CAMERA_DYNAMIC
    
    INIT_CAMERA_MP --> SETUP_LOGGING_MP[Setup Logging<br/>logs/gesture_recognition_*.log]
    INIT_CAMERA_SMOL --> SETUP_LOGGING_SMOL[Setup Logging<br/>logs/gesture_recognition_smolvlm_*.log]
    INIT_CAMERA_DYNAMIC --> SETUP_LOGGING_DYNAMIC[Setup Logging<br/>logs/engine_*.log]
    
    SETUP_LOGGING_MP --> PROCESSING_LOOP_MP[Processing Loop]
    SETUP_LOGGING_SMOL --> PROCESSING_LOOP_SMOL[Processing Loop]
    SETUP_LOGGING_DYNAMIC --> PROCESSING_LOOP_DYNAMIC[Processing Loop]
    
    PROCESSING_LOOP_MP --> CAPTURE_FRAME_MP[Capture Frame at 1 FPS]
    PROCESSING_LOOP_SMOL --> CAPTURE_FRAME_SMOL[Capture Frame at 1 FPS]
    PROCESSING_LOOP_DYNAMIC --> CAPTURE_FRAME_DYNAMIC[Capture Frame at 1 FPS]
    
    CAPTURE_FRAME_MP --> TIMER_MP{Frames Ready?<br/>1 second passed}
    CAPTURE_FRAME_SMOL --> TIMER_SMOL{Frames Ready?<br/>1 second passed}
    CAPTURE_FRAME_DYNAMIC --> TIMER_DYNAMIC{Frames Ready?<br/>1 second passed}
    
    TIMER_MP -->|No| PROCESSING_LOOP_MP
    TIMER_SMOL -->|No| PROCESSING_LOOP_SMOL
    TIMER_DYNAMIC -->|No| PROCESSING_LOOP_DYNAMIC
    
    TIMER_MP -->|Yes| PROCESS_MP[Process with MediaPipe<br/>- Detect hands<br/>- Count fingers<br/>- Detect gestures]
    TIMER_SMOL -->|Yes| PROCESS_SMOL[Process with SmolVLM<br/>- AI vision analysis<br/>- Parse response<br/>- Extract gesture info]
    TIMER_DYNAMIC -->|Yes| PROCESS_DYNAMIC[Process Current Approach]
    
    PROCESS_MP --> DRAW_MP[Draw Annotations<br/>Landmarks, Labels]
    PROCESS_SMOL --> DRAW_SMOL[Draw Annotations<br/>Detections, AI Response]
    PROCESS_DYNAMIC --> COLLECT_METRICS[Collect Metrics:<br/>Latency, CPU, Memory, FPS]
    
    DRAW_MP --> DISPLAY_MP[Display Frame]
    DRAW_SMOL --> DISPLAY_SMOL[Display Frame]
    COLLECT_METRICS --> CHECK_THRESHOLDS{Check Dynamic<br/>Thresholds}
    
    CHECK_THRESHOLDS -->|Within Limits| DISPLAY_DYNAMIC[Display Frame]
    CHECK_THRESHOLDS -->|Exceeded + Cooldown Passed| SWITCH[Switch Approach]
    
    SWITCH --> SWITCH_DECISION{Current Approach?}
    SWITCH_DECISION -->|MediaPipe| LOAD_SMOL_DYNAMIC
    SWITCH_DECISION -->|SmolVLM| LOAD_MP_DYNAMIC
    
    DISPLAY_MP --> LOG_MP[Log Results]
    DISPLAY_SMOL --> LOG_SMOL[Log Results]
    DISPLAY_DYNAMIC --> LOG_DYNAMIC[Log Results]
    
    LOG_MP --> CHECK_QUIT_MP{User Pressed<br/>'q'?}
    LOG_SMOL --> CHECK_QUIT_SMOL{User Pressed<br/>'q'?}
    LOG_DYNAMIC --> CHECK_QUIT_DYNAMIC{User Pressed<br/>'q'?}
    
    CHECK_QUIT_MP -->|No| PROCESSING_LOOP_MP
    CHECK_QUIT_SMOL -->|No| PROCESSING_LOOP_SMOL
    CHECK_QUIT_DYNAMIC -->|No| PROCESSING_LOOP_DYNAMIC
    
    CHECK_QUIT_MP -->|Yes| CLEANUP_MP[Release Camera<br/>Destroy Windows<br/>Close Hands Model]
    CHECK_QUIT_SMOL -->|Yes| CLEANUP_SMOL[Release Camera<br/>Destroy Windows]
    CHECK_QUIT_DYNAMIC -->|Yes| CLEANUP_DYNAMIC[Release Camera<br/>Destroy Windows<br/>Stop Monitor]
    
    CLEANUP_MP --> END([End])
    CLEANUP_SMOL --> END
    CLEANUP_DYNAMIC --> END
    
    style STATIC_PATH fill:#e1f5ff
    style DYNAMIC_PATH fill:#fff5e1
    style PROCESS_MP fill:#90EE90
    style PROCESS_SMOL fill:#FFB347
    style SWITCH fill:#FF6B6B
```

## Execution Summary

### Static Mode - MediaPipe
1. Load config → Read mode="static", approach="mediapipe"
2. Initialize MediaPipe hands detector
3. Setup camera and logging
4. Process frames at 1 FPS
5. Detect hands, count fingers, classify gestures
6. Display and log results
7. Exit on 'q' press

### Static Mode - SmolVLM
1. Load config → Read mode="static", approach="smolvlm"
2. Load SmolVLM model
3. Setup camera and logging
4. Process frames at 1 FPS
5. Query SmolVLM, parse AI response
6. Display and log results
7. Exit on 'q' press

### Dynamic Mode
1. Load config → Read mode="dynamic"
2. Initialize performance monitor with thresholds
3. Load starting approach (mediapipe or smolvlm)
4. Setup camera and logging
5. Process frames at 1 FPS
6. Monitor performance metrics continuously
7. Switch approach if thresholds exceeded
8. Display and log results
9. Exit on 'q' press
