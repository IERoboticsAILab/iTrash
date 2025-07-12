#!/usr/bin/env python3
"""
Continuous Camera Viewer for iTrash system.
Shows a live camera feed with controls and information overlay.
"""

import cv2
import time
import threading
import numpy as np
from datetime import datetime
from config.settings import HardwareConfig

class CameraViewer:
    """Continuous camera viewer with controls"""
    
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.is_running = False
        self.window_name = "iTrash Camera Viewer"
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()
        
        # Camera settings
        self.frame_width = HardwareConfig.FRAME_WIDTH
        self.frame_height = HardwareConfig.FRAME_HEIGHT
        self.fps_target = HardwareConfig.CAMERA_FPS
        
        # Display settings
        self.show_info = True
        self.show_fps = True
        self.show_timestamp = True
        self.show_controls = True
        
        # Recording settings
        self.is_recording = False
        self.recording_start_time = None
        self.video_writer = None
        
    def initialize_camera(self):
        """Initialize the camera"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"❌ Error: Could not open camera at index {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps_target)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Additional Raspberry Pi optimizations
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            # Test camera
            ret, test_frame = self.cap.read()
            if not ret:
                print("❌ Error: Could not read test frame from camera")
                return False
            
            print("✅ Camera initialized successfully")
            print(f"   Resolution: {self.frame_width}x{self.frame_height}")
            print(f"   Target FPS: {self.fps_target}")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing camera: {e}")
            return False
    
    def add_overlay(self, frame):
        """Add information overlay to the frame"""
        overlay = frame.copy()
        height, width = frame.shape[:2]
        
        # Calculate FPS
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
        self.frame_count += 1
        
        # Add title
        if self.show_info:
            cv2.putText(overlay, "iTrash Camera Viewer", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add FPS
        if self.show_fps:
            fps_text = f"FPS: {self.fps}"
            cv2.putText(overlay, fps_text, (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add timestamp
        if self.show_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(overlay, timestamp, (10, height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Add recording indicator
        if self.is_recording:
            recording_time = time.time() - self.recording_start_time
            recording_text = f"REC {recording_time:.1f}s"
            cv2.putText(overlay, recording_text, (width - 150, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # Add red border
            cv2.rectangle(overlay, (0, 0), (width-1, height-1), (0, 0, 255), 3)
        
        # Add controls info
        if self.show_controls:
            controls = [
                "Controls:",
                "R - Start/Stop Recording",
                "S - Save Screenshot",
                "I - Toggle Info Overlay",
                "F - Toggle FPS Display",
                "T - Toggle Timestamp",
                "C - Toggle Controls",
                "Q - Quit"
            ]
            
            y_offset = 100
            for control in controls:
                cv2.putText(overlay, control, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                y_offset += 20
        
        return overlay
    
    def save_screenshot(self, frame):
        """Save a screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.jpg"
        try:
            cv2.imwrite(filename, frame)
            print(f"✅ Screenshot saved: {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to save screenshot: {e}")
            return False
    
    def start_recording(self):
        """Start video recording"""
        if self.is_recording:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.mp4"
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                filename, fourcc, self.fps_target, 
                (self.frame_width, self.frame_height)
            )
            self.is_recording = True
            self.recording_start_time = time.time()
            print(f"✅ Recording started: {filename}")
        except Exception as e:
            print(f"❌ Failed to start recording: {e}")
    
    def stop_recording(self):
        """Stop video recording"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        recording_duration = time.time() - self.recording_start_time
        print(f"✅ Recording stopped: {recording_duration:.1f} seconds")
    
    def handle_key_press(self, key):
        """Handle key press events"""
        if key == ord('q') or key == ord('Q'):
            return False  # Quit
        elif key == ord('r') or key == ord('R'):
            if self.is_recording:
                self.stop_recording()
            else:
                self.start_recording()
        elif key == ord('s') or key == ord('S'):
            # Save screenshot (will be handled in main loop)
            pass
        elif key == ord('i') or key == ord('I'):
            self.show_info = not self.show_info
        elif key == ord('f') or key == ord('F'):
            self.show_fps = not self.show_fps
        elif key == ord('t') or key == ord('T'):
            self.show_timestamp = not self.show_timestamp
        elif key == ord('c') or key == ord('C'):
            self.show_controls = not self.show_controls
        return True  # Continue
    
    def run(self):
        """Run the camera viewer"""
        if not self.initialize_camera():
            return False
        
        # Create window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 800, 600)
        
        print("🎥 Camera viewer started")
        print("   Press 'R' to start/stop recording")
        print("   Press 'S' to save screenshot")
        print("   Press 'Q' to quit")
        
        self.is_running = True
        
        try:
            while self.is_running:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Failed to read frame from camera")
                    break
                
                # Add overlay
                frame_with_overlay = self.add_overlay(frame)
                
                # Write to recording if active
                if self.is_recording and self.video_writer:
                    self.video_writer.write(frame)  # Write original frame without overlay
                
                # Display frame
                cv2.imshow(self.window_name, frame_with_overlay)
                
                # Handle key press
                key = cv2.waitKey(1) & 0xFF
                if key != 255:  # Key was pressed
                    if key == ord('s') or key == ord('S'):
                        self.save_screenshot(frame)
                    elif not self.handle_key_press(key):
                        break
                
                # Small delay to prevent high CPU usage
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n👋 Camera viewer interrupted")
        except Exception as e:
            print(f"❌ Camera viewer error: {e}")
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """Clean up resources"""
        self.is_running = False
        
        if self.is_recording:
            self.stop_recording()
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        print("✅ Camera viewer cleaned up")

def main():
    """Main function"""
    print("🎥 iTrash Camera Viewer")
    print("=" * 30)
    
    viewer = CameraViewer()
    
    try:
        viewer.run()
    except Exception as e:
        print(f"💥 Camera viewer failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 