#!/usr/bin/env python3
"""
Simple test function for the current GPT classifier
"""

import cv2
import numpy as np
from core.ai_classifier import GPTClassifier
from config.settings import OPENAI_API_KEY

def test_gpt_classifier():
    """Test the current GPT classifier with a captured camera image"""
    
    # Check if API key is available
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in .env file")
        return False
    
    print("🧪 Testing GPT Classifier...")
    print(f"📝 Using model: gpt-4o-mini")
    print(f"🔑 API Key: {'*' * 10 + OPENAI_API_KEY[-4:] if OPENAI_API_KEY else 'Not set'}")
    
    # Try to capture image from camera
    print("📷 Attempting to capture image from camera...")
    cap = cv2.VideoCapture(0)  # Try camera index 0
    
    if not cap.isOpened():
        print("❌ Could not open camera. Trying alternative camera index...")
        cap = cv2.VideoCapture(1)  # Try camera index 1
        
    if not cap.isOpened():
        print("❌ Could not open any camera. Creating test image instead...")
        # Fallback to test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:, :] = (255, 0, 0)  # Blue in BGR
        print(f"🖼️  Created test image: {test_image.shape} (Blue rectangle)")
    else:
        print("✅ Camera opened successfully")
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Capture frame
        ret, test_image = cap.read()
        if ret:
            print(f"📸 Captured image: {test_image.shape}")
            print("💡 Place a trash item in front of the camera and press any key to capture...")
            
            # Show preview window
            cv2.imshow('Camera Preview - Press any key to capture', test_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            # Capture final image
            ret, test_image = cap.read()
            if ret:
                print("✅ Image captured successfully!")
            else:
                print("❌ Failed to capture image")
                cap.release()
                return False
        else:
            print("❌ Failed to read from camera")
            cap.release()
            return False
        
        cap.release()
    
    # Save captured image for reference
    try:
        cv2.imwrite('test_captured_image.jpg', test_image)
        print("💾 Saved captured image as 'test_captured_image.jpg'")
    except Exception as e:
        print(f"⚠️  Could not save image: {e}")
    
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
        print(f"🎯 Result: {result}")
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

def test_with_saved_image(image_path):
    """Test with a saved image file"""
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not available")
        return False
    
    print(f"\n📁 Testing with saved image: {image_path}")
    
    # Load image
    try:
        test_image = cv2.imread(image_path)
        if test_image is None:
            print(f"❌ Could not load image: {image_path}")
            return False
        
        print(f"📸 Loaded image: {test_image.shape}")
        
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return False
    
    # Test classification
    try:
        classifier = GPTClassifier()
        result = classifier.classify(test_image)
        
        print(f"🎯 Classification result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Error during classification: {e}")
        return False

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
    import sys
    
    print("🚀 Starting GPT Classifier Test")
    print("=" * 50)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--saved" and len(sys.argv) > 2:
            # Test with saved image
            image_path = sys.argv[2]
            test_with_saved_image(image_path)
        elif sys.argv[1] == "--colors":
            # Test with colored rectangles
            test_with_different_colors()
        else:
            print("Usage:")
            print("  python test_gpt_classifier.py              # Test with camera capture")
            print("  python test_gpt_classifier.py --saved <path>  # Test with saved image")
            print("  python test_gpt_classifier.py --colors       # Test with colored rectangles")
    else:
        # Default: test with camera capture
        success = test_gpt_classifier()
        
        if success:
            print("\n💡 You can also test with:")
            print("  python test_gpt_classifier.py --saved test_captured_image.jpg")
            print("  python test_gpt_classifier.py --colors")
    
    print("\n" + "=" * 50)
    print("🏁 Test session completed") 