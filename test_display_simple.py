#!/usr/bin/env python3
"""
Simple display test for iTrash system.
Tests the display system without the full application.
"""

import time
import sys
from display.media_display import DisplayManager

def main():
    """Test the display system"""
    print("🖥️  Testing Display System")
    print("=" * 30)
    
    try:
        # Create display manager
        manager = DisplayManager()
        print("✅ Display manager created")
        
        # Check status before starting
        status = manager.get_display_status()
        print(f"   Status before start: {status}")
        
        # Start display in a separate thread
        import threading
        display_thread = threading.Thread(target=manager.start_display, daemon=True)
        display_thread.start()
        
        print("✅ Display started in background")
        print("   You should see a display window appear")
        print("   Press 'f' to toggle fullscreen")
        print("   Press 'q' to quit")
        print("   Click mouse to quit")
        
        # Wait a bit for display to initialize
        time.sleep(2)
        
        # Check status after starting
        status = manager.get_display_status()
        print(f"   Status after start: {status}")
        
        # Keep running for 10 seconds
        print("   Display will run for 10 seconds...")
        time.sleep(10)
        
        # Stop display
        manager.stop_display()
        print("✅ Display stopped")
        
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        return False
    
    print("✅ Display test completed successfully")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Display test interrupted")
    except Exception as e:
        print(f"💥 Display test failed: {e}") 