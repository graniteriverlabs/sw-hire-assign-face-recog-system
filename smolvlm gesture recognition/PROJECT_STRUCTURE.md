# Project Structure Documentation

## Overview

The project has been restructured to support configuration-driven execution with both static and dynamic approach selection.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        engine.py                            │
│                  (Orchestration Layer)                      │
│                                                             │
│  • Reads JSON configuration                                 │
│  • Selects approach (static or dynamic)                     │
│  • Monitors performance (if dynamic mode)                  │
│  • Executes appropriate module                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─────────────────────┬─────────────────────┐
                 │                     │                     │
                 ▼                     ▼                     ▼
    ┌─────────────────────┐  ┌──────────────────────┐  ┌──────────────┐
    │   config.json       │  │  gesture_recognition │  │  SmolVLM     │
    │  (Configuration)    │  │  .py                │  │  .py         │
    │                     │  │                     │  │              │
    │  • Mode selection   │  │  MediaPipe          │  │  SmolVLM      │
    │  • Approach config  │  │  approach           │  │  approach    │
    │  • Performance      │  │  (Fast, lightweight)│  │  (Advanced,  │
    │    thresholds       │  │                     │  │   slower)    │
    └─────────────────────┘  └─────────────────────┘  └──────────────┘
```

## File Structure

### Configuration File

**`config.json`** - The single configuration file

The configuration file supports all modes:

- **Static Mode**: Set `mode` to `"static"` and choose `"mediapipe"` or `"smolvlm"` as the approach
- **Dynamic Mode**: Set `mode` to `"dynamic"` and configure performance thresholds

To switch between approaches, simply edit the `mode` and `approach` fields in `config.json`.

### Core Files

1. **`engine.py`**

   - Main orchestration engine
   - Reads JSON configuration
   - Executes selected approach
   - Monitors performance (dynamic mode)
   - Command-line interface for config selection
2. **`gesture_recognition.py`**

   - MediaPipe-based gesture recognition
   - Fast, lightweight, real-time capable
   - Approach 1: Static MediaPipe
3. **`gesture_recognition_smolvlm_only.py`**

   - SmolVLM-based gesture recognition
   - Advanced understanding, detailed analysis
   - Approach 2: Static SmolVLM

### Supporting Files

- **`requirements.txt`** - Python dependencies
- **`test_smolvlm.py`** - Test script for SmolVLM
- **`README.md`** - User documentation
- **`logs/`** - Log files directory

## Configuration JSON Schema

```json
{
  "mode": "static" | "dynamic",
  "approach": "mediapipe" | "smolvlm",
  "camera_index": 0,
  "frame_interval_sec": 1.0,
  "logging": {
    "enabled": true,
    "log_dir": "logs"
  },
  "dynamic": {
    "enabled": false,
    "performance_thresholds": {
      "max_latency_ms": 1000,
      "max_cpu_percent": 80,
      "max_memory_mb": 2000,
      "min_fps": 0.8
    },
    "evaluation_window_sec": 5,
    "switch_cooldown_seconds": 10
  },
  "approaches": {
    "mediapipe": {
      "module": "gesture_recognition",
      "main_function": "main"
    },
    "smolvlm": {
      "module": "gesture_recognition_smolvlm_only",
      "main_function": "main"
    }
  }
}
```

## Execution Modes

### 1. Static Mode

**Configuration in config.json:**

```json
{
  "mode": "static",
  "approach": "mediapipe"  // or "smolvlm"
}
```

**Behavior:**

- Uses the specified approach throughout execution
- No dynamic switching
- Predictable performance characteristics

**Usage:**

```bash
python engine.py
```

### 2. Dynamic Mode

**Configuration in config.json:**

```json
{
  "mode": "dynamic",
  "approach": "mediapipe",  // starting approach
  "dynamic": {
    "enabled": true,
    "performance_thresholds": { ... }
  }
}
```

**Behavior:**

- Monitors performance metrics (latency, CPU, memory, FPS)
- Automatically switches approaches if thresholds are exceeded
- Cooldown period prevents rapid switching
- Evaluation window ensures stable decisions

**Usage:**

```bash
python engine.py
```

## Approach Comparison

| Feature                    | MediaPipe | SmolVLM           |
| -------------------------- | --------- | ----------------- |
| **Speed**            | Fast      | Slower            |
| **Resources**        | Low       | High              |
| **Accuracy**         | Good      | Excellent         |
| **GPU Required**     | No        | Yes (recommended) |
| **Real-time**        | Yes       | Limited           |
| **Complex Gestures** | Basic     | Advanced          |

## Execution Flow

### Static Mode Flow

```
1. Load config.json
2. Read mode = "static"
3. Read approach = "mediapipe" or "smolvlm"
4. Import corresponding module
5. Execute main() function
6. Run gesture recognition loop
7. Exit on user interrupt
```

### Dynamic Mode Flow

```
1. Load config.json
2. Read mode = "dynamic"
3. Read starting approach
4. Initialize performance monitor
5. Import starting approach module
6. Execute main() function
7. Monitor performance metrics
8. Evaluate against thresholds
9. Switch approach if needed
10. Continue monitoring
11. Exit on user interrupt
```

## Command-Line Interface

```bash
# Basic usage (reads config.json)
python engine.py
```

## Performance Monitoring

### Metrics Tracked

1. **Latency** - Processing time per frame (ms)
2. **CPU Usage** - Percentage of CPU utilization
3. **Memory Usage** - RAM consumption (MB)
4. **FPS** - Frames per second

### Switching Logic

The dynamic mode evaluates performance over a configurable window:

- Averages metrics over N frames (evaluation_window)
- Compares against thresholds
- Switches approach if any threshold exceeded
- Applies cooldown to prevent rapid switching

### Example Thresholds

**Fast System (MediaPipe typical):**

- max_latency_ms: 100
- max_cpu_percent: 50
- max_memory_mb: 500
- min_fps: 10

**Resource-Constrained (Dynamic switching needed):**

- max_latency_ms: 1000
- max_cpu_percent: 80
- max_memory_mb: 2000
- min_fps: 0.8

## Migration Guide

### From Direct Execution

**Before:**

```bash
python gesture_recognition.py
python gesture_recognition_smolvlm_only.py
```

**After:**

```bash
# Edit config.json to choose approach, then:
python engine.py
```

### Benefits of New Structure

1. **Centralized Configuration** - All settings in JSON
2. **Flexible Execution** - Choose approach via config
3. **Dynamic Optimization** - Automatic approach switching
4. **Performance Monitoring** - Built-in metrics tracking
5. **Easier Maintenance** - Single entry point
6. **Extensibility** - Easy to add new approaches

## Extending the System

### Adding a New Approach

1. Create new module (e.g., `gesture_recognition_yolo.py`)
2. Implement `main()` function
3. Add to `config.json`:

```json
"approaches": {
  "yolo": {
    "module": "gesture_recognition_yolo",
    "main_function": "main",
    "description": "YOLO-based approach"
  }
}
```

4. Use in config:

```json
{
  "mode": "static",
  "approach": "yolo"
}
```

### Adding New Metrics

Edit `PerformanceMonitor` class in `engine.py`:

```python
def record(self, metrics: Dict[str, float]):
    # Add new metric
    self.history['new_metric'].append(metrics.get('new_metric', 0))
```

Add threshold in config:

```json
"performance_thresholds": {
  "max_new_metric": 100
}
```

## Troubleshooting

### Issue: Module Not Found

**Solution:** Ensure dependencies are installed:

```bash
pip install -r requirements.txt
```

### Issue: Config File Not Found

**Solution:** Create config.json in the project root directory

### Issue: Dynamic Mode Not Working

**Solution:** Verify `dynamic.enabled` is true in config

### Issue: Performance Monitors Not Accurate

**Solution:** Increase `evaluation_window` for more stable measurements

## Summary

The new structure provides:

- ✅ JSON-based configuration
- ✅ Static approach selection
- ✅ Dynamic performance-based switching
- ✅ Unified execution via `engine.py`
- ✅ Extensible architecture
- ✅ Performance monitoring
- ✅ Command-line interface
