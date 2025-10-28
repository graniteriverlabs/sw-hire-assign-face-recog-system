"""
Quick test script to verify SmolVLM can be loaded
"""

import torch
from transformers import AutoProcessor, AutoModelForVision2Seq

print("=" * 60)
print("Testing SmolVLM Model Loading")
print("=" * 60)

print("\nChecking PyTorch...")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")

print("\nAttempting to load SmolVLM...")
print("This will download the model (~1.5GB) on first run")
print("Model: HuggingFaceTB/SmolVLM-Instruct")

try:
    model_name = "HuggingFaceTB/SmolVLM-Instruct"
    
    print("\n1. Loading processor...")
    processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
    print("   ✓ Processor loaded!")
    
    print("\n2. Loading model...")
    if torch.cuda.is_available():
        print(f"   Using GPU: {torch.cuda.get_device_name(0)}")
        model = AutoModelForVision2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
    else:
        print("   Using CPU (slower)")
        model = AutoModelForVision2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            trust_remote_code=True
        )
    
    print("   ✓ Model loaded!")
    
    print("\n" + "=" * 60)
    print("✓ Success! SmolVLM is ready to use")
    print(f"Model device: {next(model.parameters()).device}")
    print("=" * 60)
    print("\nYou can now run: python gesture_recognition_smolvlm_only.py")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ Error loading SmolVLM")
    print("=" * 60)
    print(f"\nError: {e}")
    print("\nTroubleshooting:")
    print("1. Check internet connection")
    print("2. Verify installation: pip install transformers torch")
    print("3. Try again in a few moments (server might be busy)")
    print("\nFor detailed error info, run with: python -u test_smolvlm.py")
    import sys
    import traceback
    traceback.print_exc()
    sys.exit(1)

