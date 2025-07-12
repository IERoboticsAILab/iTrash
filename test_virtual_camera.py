#!/usr/bin/env python3
"""
Test script for virtual camera display.
Tests the continuous camera feed in a separate window.
"""

import time
import sys
import cv2
from core.camera import CameraController

def test_virtual_camera():
    """Test virtual camera display"""
    print("📷 Testing Virtual Camera Display")
    print("=" * 40)
    
    try:
        # Initialize camera
        camera = CameraController()
        if not camera.initialize():
            print("❌ Failed to initialize camera")
            return False
        
        print("✅ Camera initialized")
        
        # Create virtual display window
        window_name = "Virtual Camera Test"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 800, 600)
        
        print(f"✅ Virtual display window created: {window_name}")
        print("   Press 'q' in camera window to close")
        print("   Press 's' to save current frame")
        print("   Press 'r' to reset window size")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            try:
                # Read frame
                ret, frame = camera.read_frame()
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                # Add overlay information
                overlay = frame.copy()
                
                # Add title
                cv2.putText(overlay, "Virtual Camera Test", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Add frame info
                frame_count += 1
                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time if elapsed_time > 0 else 0
                
                info_text = f"Frame: {frame_count}, FPS: {fps:.1f}, Size: {frame.shape[1]}x{frame.shape[0]}"
                cv2.putText(overlay, info_text, (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                
                # Add controls info
                controls_text = "Controls: q=quit, s=save, r=reset"
                cv2.putText(overlay, controls_text, (10, overlay.shape[0] - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Display frame
                cv2.imshow(window_name, overlay)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("   Quit requested")
                    break
                elif key == ord('s'):
                    # Save current frame
                    filename = f"test_frame_{int(time.time())}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"   Frame saved as {filename}")
                elif key == ord('r'):
                    # Reset window size
                    cv2.resizeWindow(window_name, 800, 600)
                    print("   Window size reset")
                
            except Exception as e:
                print(f"❌ Error in camera loop: {e}")
                break
        
        # Cleanup
        cv2.destroyAllWindows()
        camera.release()
        
        print("✅ Virtual camera test completed")
        print(f"   Total frames: {frame_count}")
        print(f"   Average FPS: {frame_count / elapsed_time:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Virtual camera test failed: {e}")
        return False

def main():
    """Main function"""
    try:
        return test_virtual_camera()
    except KeyboardInterrupt:
        print("\n👋 Virtual camera test interrupted")
        return False
    except Exception as e:
        print(f"💥 Virtual camera test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 