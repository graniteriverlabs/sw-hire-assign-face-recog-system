"""
Gesture Recognition Engine
Reads configuration from JSON and executes the appropriate approach
Supports static and dynamic mode selection
"""

import json
import sys
import os
import importlib
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading

# Configure logging
def setup_logging(config: Dict[str, Any]):
    """Setup logging based on configuration"""
    log_dir = Path(config.get('logging', {}).get('log_dir', 'logs'))
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"engine_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration parameters"""
    # Validate mode
    if config.get('mode') not in ['static', 'dynamic']:
        print("Error: 'mode' must be 'static' or 'dynamic'")
        return False
    
    # If static, validate approach
    if config.get('mode') == 'static':
        approach = config.get('approach')
        if approach not in ['mediapipe', 'smolvlm']:
            print(f"Error: Invalid approach '{approach}'. Must be 'mediapipe' or 'smolvlm'")
            return False
        
        # Validate that the approach is configured
        if approach not in config.get('approaches', {}):
            print(f"Error: Approach '{approach}' not found in configuration")
            return False
    
    # If dynamic, validate dynamic settings
    if config.get('mode') == 'dynamic':
        dynamic_config = config.get('dynamic', {})
        if not dynamic_config.get('enabled'):
            print("Error: Dynamic mode is set but 'dynamic.enabled' is False")
            return False
    
    return True


class PerformanceMonitor:
    """Monitor performance metrics for dynamic switching"""
    
    def __init__(self, thresholds: Dict[str, float], window_size: int = 5):
        self.thresholds = thresholds
        self.window_size = window_size
        self.history = {
            'latency_ms': [],
            'cpu_percent': [],
            'memory_mb': [],
            'fps': []
        }
    
    def record(self, metrics: Dict[str, float]):
        """Record performance metrics"""
        self.history['latency_ms'].append(metrics.get('latency_ms', 0))
        self.history['cpu_percent'].append(metrics.get('cpu_percent', 0))
        self.history['memory_mb'].append(metrics.get('memory_mb', 0))
        self.history['fps'].append(metrics.get('fps', 0))
        
        # Keep only window_size recent records
        for key in self.history:
            if len(self.history[key]) > self.window_size:
                self.history[key] = self.history[key][-self.window_size:]
    
    def get_average_metrics(self) -> Dict[str, float]:
        """Get average metrics over the evaluation window"""
        return {
            'latency_ms': sum(self.history['latency_ms']) / len(self.history['latency_ms']) if self.history['latency_ms'] else 0,
            'cpu_percent': sum(self.history['cpu_percent']) / len(self.history['cpu_percent']) if self.history['cpu_percent'] else 0,
            'memory_mb': sum(self.history['memory_mb']) / len(self.history['memory_mb']) if self.history['memory_mb'] else 0,
            'fps': sum(self.history['fps']) / len(self.history['fps']) if self.history['fps'] else 0
        }
    
    def should_switch(self) -> bool:
        """Determine if approach should be switched based on thresholds"""
        if len(self.history['latency_ms']) < self.window_size:
            return False
        
        avg = self.get_average_metrics()
        
        # Check if any threshold is exceeded
        if avg['latency_ms'] > self.thresholds.get('max_latency_ms', 1000):
            return True
        if avg['cpu_percent'] > self.thresholds.get('max_cpu_percent', 80):
            return True
        if avg['memory_mb'] > self.thresholds.get('max_memory_mb', 2000):
            return True
        if avg['fps'] < self.thresholds.get('min_fps', 0.8):
            return True
        
        return False


class GestureRecognitionEngine:
    """Main engine for gesture recognition"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logging(config)
        self.current_approach = None
        self.performance_monitor = None
        
        # Initialize performance monitor if dynamic mode
        if config.get('mode') == 'dynamic':
            thresholds = config.get('dynamic', {}).get('performance_thresholds', {})
            window_size = config.get('dynamic', {}).get('evaluation_window', 5)
            self.performance_monitor = PerformanceMonitor(thresholds, window_size)
            self.last_switch_time = 0
            self.switch_cooldown = config.get('dynamic', {}).get('switch_cooldown_seconds', 10)
    
    def get_available_approaches(self) -> List[str]:
        """Get list of available approaches"""
        return list(self.config.get('approaches', {}).keys())
    
    def switch_approach(self, from_approach: str, to_approach: str) -> bool:
        """Switch from one approach to another"""
        if to_approach not in self.get_available_approaches():
            self.logger.error(f"Invalid approach: {to_approach}")
            return False
        
        # Check cooldown period
        if self.config.get('mode') == 'dynamic':
            current_time = time.time()
            if current_time - self.last_switch_time < self.switch_cooldown:
                self.logger.warning(f"Switch on cooldown. Need to wait {self.switch_cooldown} seconds")
                return False
        
        self.logger.info(f"Switching from {from_approach} to {to_approach}")
        self.current_approach = to_approach
        
        if self.config.get('mode') == 'dynamic':
            self.last_switch_time = time.time()
        
        return True
    
    def should_switch_dynamically(self) -> Optional[str]:
        """Determine if we should switch approaches in dynamic mode"""
        if self.config.get('mode') != 'dynamic' or not self.performance_monitor:
            return None
        
        if self.performance_monitor.should_switch():
            # Switch to the other approach
            available_approaches = self.get_available_approaches()
            other_approach = [a for a in available_approaches if a != self.current_approach][0]
            return other_approach
        
        return None
    
    def execute_static_mode(self) -> None:
        """Execute in static mode with predetermined approach"""
        approach = self.config.get('approach')
        self.current_approach = approach
        
        self.logger.info(f"Static mode: Executing {approach} approach")
        
        # Get approach configuration
        approach_config = self.config.get('approaches', {}).get(approach, {})
        module_name = approach_config.get('module')
        main_function = approach_config.get('main_function', 'main')
        
        if not module_name:
            self.logger.error(f"No module specified for approach: {approach}")
            return
        
        # Import and execute the module
        try:
            self.logger.info(f"Importing module: {module_name}")
            module = importlib.import_module(module_name)
            
            if not hasattr(module, main_function):
                self.logger.error(f"Module {module_name} has no function '{main_function}'")
                return
            
            # Execute the main function
            self.logger.info(f"Executing {module_name}.{main_function}()")
            main_func = getattr(module, main_function)
            main_func()
            
        except ImportError as e:
            self.logger.error(f"Failed to import module '{module_name}': {e}")
        except Exception as e:
            self.logger.error(f"Error executing {module_name}.{main_function}(): {e}")
            import traceback
            traceback.print_exc()
    
    def execute_dynamic_mode(self) -> None:
        """Execute in dynamic mode with automatic switching"""
        # Start with the first approach
        self.current_approach = self.config.get('approach', 'mediapipe')
        
        self.logger.info(f"Dynamic mode: Starting with {self.current_approach} approach")
        self.logger.info("Will automatically switch if performance degrades")
        
        # This is a simplified version - in production, you'd want a more sophisticated
        # implementation that can actually switch between approaches during runtime
        
        # For now, we'll monitor the first approach and log when switching would occur
        self.logger.warning("Dynamic mode is limited in this implementation")
        self.logger.warning("Full dynamic switching requires architecture changes to the processing modules")
        
        # For now, just execute the starting approach
        self.execute_static_mode()
    
    def execute(self) -> None:
        """Execute the engine based on configuration"""
        mode = self.config.get('mode')
        
        if mode == 'static':
            self.execute_static_mode()
        elif mode == 'dynamic':
            self.execute_dynamic_mode()
        else:
            self.logger.error(f"Unknown mode: {mode}")
            sys.exit(1)


def main():
    """Main entry point"""
    # Load configuration
    config = load_config()
    
    # Validate configuration
    if not validate_config(config):
        print("Configuration validation failed")
        sys.exit(1)
    
    # Create and execute engine
    engine = GestureRecognitionEngine(config)
    
    print("=" * 60)
    print("Gesture Recognition Engine")
    print("=" * 60)
    print(f"Mode: {config.get('mode', 'unknown').upper()}")
    if config.get('mode') == 'static':
        print(f"Approach: {config.get('approach', 'unknown')}")
    elif config.get('mode') == 'dynamic':
        print(f"Initial Approach: {config.get('approach', 'unknown')}")
        print("Dynamic switching: ENABLED")
    print("=" * 60)
    print()
    
    try:
        engine.execute()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

