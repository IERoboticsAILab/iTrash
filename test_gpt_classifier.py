#!/usr/bin/env python3
"""
Simple test function for the current GPT classifier
"""

import cv2
import numpy as np
from core.ai_classifier import GPTClassifier
from config.settings import OPENAI_API_KEY

def test_gpt_classifier():
    """Test the current GPT classifier with a simple colored image"""
    
    # Check if API key is available
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in .env file")
        return False
    
    print("🧪 Testing GPT Classifier...")
    print(f"📝 Using model: gpt-4o-mini")
    print(f"🔑 API Key: {'*' * 10 + OPENAI_API_KEY[-4:] if OPENAI_API_KEY else 'Not set'}")
    
    # Create a simple test image (blue rectangle)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    # Fill with blue color (BGR format in OpenCV)
    test_image[:, :] = (255, 0, 0)  # Blue in BGR
    
    print(f"🖼️  Created test image: {test_image.shape} (Blue rectangle)")
    
    # Initialize the classifier
    try:
        classifier = GPTClassifier()
        print("✅ GPT Classifier initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing classifier: {e}")
        return False
    
    # Test classification
    try:
        print("🔄 Sending image to GPT for classification...")
        result = classifier.classify(test_image)
        
        if result:
            print(f"✅ Classification successful!")
            print(f"🎯 Result: {result}")
            print(f"📦 Expected: blue (since we sent a blue image)")
            
            if result == "blue":
                print("🎉 Perfect! GPT correctly identified the blue color")
            else:
                print(f"🤔 Interesting! GPT returned '{result}' instead of 'blue'")
        else:
            print("❌ Classification failed - no result returned")
            return False
            
    except Exception as e:
        print(f"❌ Error during classification: {e}")
        return False
    
    print("\n🎊 Test completed successfully!")
    return True

def test_with_different_colors():
    """Test with different colored rectangles"""
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not available")
        return
    
    print("\n🌈 Testing with different colors...")
    
    # Color definitions (BGR format)
    test_colors = {
        "blue": (255, 0, 0),
        "yellow": (0, 255, 255), 
        "brown": (19, 69, 139)
    }
    
    classifier = GPTClassifier()
    
    for color_name, bgr_color in test_colors.items():
        print(f"\n🎨 Testing {color_name}...")
        
        # Create colored rectangle
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:, :] = bgr_color
        
        try:
            result = classifier.classify(test_image)
            print(f"   Result: {result}")
            print(f"   Expected: {color_name}")
            print(f"   ✅ Correct!" if result == color_name else f"   ❌ Wrong!")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting GPT Classifier Test")
    print("=" * 50)
    
    # Run basic test
    success = test_gpt_classifier()
    
    if success:
        # Run color tests
        test_with_different_colors()
    
    print("\n" + "=" * 50)
    print("🏁 Test session completed") 