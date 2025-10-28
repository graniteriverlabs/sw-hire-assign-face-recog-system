# Gesture Recognition System

A flexible gesture recognition system with multiple approaches and dynamic configuration.

## Project Structure

```
├── config.json                          # Configuration file (static/dynamic modes)
├── engine.py                            # Main engine that reads config and executes
├── gesture_recognition.py              # MediaPipe-based approach (fast, lightweight)
├── gesture_recognition_smolvlm_only.py # SmolVLM-based approach (advanced, slower)
├── test_smolvlm.py                     # Test script for SmolVLM
├── requirements.txt                     # Python dependencies
├── flowchart.md                        # Execution flowcharts
├── architecture.md                     # Architecture diagrams
├── dataflow.md                         # Data flow diagrams
└── logs/                                # Log files directory
```

## Documentation

- **README.md** - This file - User guide and usage instructions
- **PROJECT_STRUCTURE.md** - Detailed architecture documentation
- **flowchart.md** - Execution flowchart showing how the system runs
- **architecture.md** - Architecture diagrams showing system structure
- **dataflow.md** - Data flow diagrams showing how data moves through the system

## Configuration

The `config.json` file is the single source of configuration for the entire system.

### Static Mode

Use a fixed approach by setting:

```json
{
  "mode": "static",
  "approach": "mediapipe"  // or "smolvlm"
}
```

### Dynamic Mode

Enable automatic switching between approaches based on performance:

```json
{
  "mode": "dynamic",
  "approach": "mediapipe",
  "dynamic": {
    "enabled": true,
    "performance_thresholds": {
      "max_latency_ms": 1000,
      "max_cpu_percent": 80,
      "max_memory_mb": 2000,
      "min_fps": 0.8
    },
    "evaluation_window": 5,
    "switch_cooldown_seconds": 10
  }
}
```

When performance thresholds are exceeded, the system automatically switches to the other approach.

## Usage

### Basic Usage

Run the engine with the default configuration:

```bash
python engine.py
```

The engine will:
1. Read `config.json`
2. Load the specified approach (MediaPipe or SmolVLM)
3. Execute the gesture recognition system
4. Monitor performance (if in dynamic mode)

### Changing Approaches

To switch between approaches, edit `config.json`:

**For MediaPipe (Fast):**
```json
{
  "mode": "static",
  "approach": "mediapipe"
}
```

**For SmolVLM (Advanced):**
```json
{
  "mode": "static",
  "approach": "smolvlm"
}
```

**For Dynamic Mode (Auto-switching):**
```json
{
  "mode": "dynamic",
  "approach": "mediapipe",
  "dynamic": {
    "enabled": true,
    ...
  }
}
```

### Dynamic Mode

Set dynamic mode in `config.json`:

```json
{
  "mode": "dynamic",
  "approach": "mediapipe",
  "dynamic": {
    "enabled": true,
    ...
  }
}
```

In dynamic mode, the system will:
- Start with the specified approach
- Monitor performance metrics
- Automatically switch if thresholds are exceeded

## Approaches

### MediaPipe (gesture_recognition.py)

- **Speed**: Fast (real-time capable)
- **Resource Usage**: Low CPU/memory
- **Accuracy**: Good for basic gestures
- **Best For**: General use, low-resource systems

### SmolVLM (gesture_recognition_smolvlm_only.py)

- **Speed**: Slower (requires GPU for best performance)
- **Resource Usage**: High CPU/memory (GPU recommended)
- **Accuracy**: Advanced understanding
- **Best For**: Complex gestures, detailed analysis

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. For SmolVLM, you may need additional packages:
```bash
pip install torch transformers accelerate
```

## Configuration Options

### General Options

- `mode`: `"static"` or `"dynamic"`
- `approach`: `"mediapipe"` or `"smolvlm"`
- `camera_index`: Camera device index (default: 0)
- `frame_interval`: Seconds between frames (default: 1.0)

### Performance Thresholds (Dynamic Mode)

- `max_latency_ms`: Maximum processing latency in milliseconds
- `max_cpu_percent`: Maximum CPU usage percentage
- `max_memory_mb`: Maximum memory usage in MB
- `min_fps`: Minimum frames per second

### Switching Parameters (Dynamic Mode)

- `evaluation_window`: Number of frames to evaluate before switching
- `switch_cooldown_seconds`: Wait time between switches

## Logging

Logs are written to the `logs/` directory with timestamps:
- `engine_YYYYMMDD_HHMMSS.log` - Engine execution logs
- `gesture_recognition_YYYYMMDD_HHMMSS.log` - MediaPipe logs
- `gesture_recognition_smolvlm_YYYYMMDD_HHMMSS.log` - SmolVLM logs

## Troubleshooting

### Module Import Errors

If you get import errors, make sure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Camera Issues

If the camera doesn't open:
1. Check `camera_index` in config (try 1, 2, etc.)
2. Ensure camera is not in use by another application

### SmolVLM Slow Performance

SmolVLM requires:
- GPU with CUDA support (recommended)
- OR sufficient CPU resources

For best performance, use a GPU with CUDA support.

## Examples

### Example 1: Run with MediaPipe (Fast)

```bash
# Edit config.json to set:
{
  "mode": "static",
  "approach": "mediapipe"
}

# Run
python engine.py
```

### Example 2: Run with SmolVLM (Advanced)

```bash
# Edit config.json to set:
{
  "mode": "static",
  "approach": "smolvlm"
}

# Run
python engine.py
```

### Example 3: Dynamic Mode

```bash
# Edit config.json to set:
{
  "mode": "dynamic",
  "approach": "mediapipe",
  "dynamic": {
    "enabled": true,
    "performance_thresholds": { ... }
  }
}

# Run
python engine.py
```

### Example 4: Direct Module Execution

You can also run the modules directly without the engine:

```bash
# Run MediaPipe approach directly
python gesture_recognition.py

# Run SmolVLM approach directly
python gesture_recognition_smolvlm_only.py
```

## License

This project is provided as-is for gesture recognition purposes.

