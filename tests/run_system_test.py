#!/usr/bin/env python3
"""
Run the actual iTrash unified system with fullscreen display integration.
This tests the real system, not just components.
"""

import time
import sys
import signal
import threading
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Received signal {signum}, shutting down...")
    sys.exit(0)

def run_system():
    """Run the complete iTrash system"""
    print("🚀 Starting iTrash Unified System with Fullscreen Display")
    print("=" * 60)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Import the unified system
        from unified_main import create_app, lifespan
        from display.media_display import DisplayManager
        from global_state import state
        
        print("🔧 Initializing system components...")
        
        # Create the FastAPI app
        app = create_app()
        print("✅ FastAPI application created")
        
        # Start the lifespan context
        lifespan_context = lifespan(app)
        
        # Start the system
        print("🚀 Starting system...")
        
        # Run the startup
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Start the lifespan
        lifespan_gen = lifespan_context.__aenter__()
        loop.run_until_complete(lifespan_gen)
        
        print("✅ System started successfully!")
        print("🎯 System is now running with fullscreen display")
        print("💡 The display will show images based on system state")
        print("💡 Press Ctrl+C to stop the system")
        
        # Test state changes
        print("\n🧪 Testing state changes...")
        test_phases = [
            ("idle", "System ready"),
            ("processing", "Processing trash"),
            ("show_trash", "Showing classification"),
            ("user_confirmation", "Waiting for user"),
            ("reward", "Success!")
        ]
        
        for phase, description in test_phases:
            print(f"📸 {description} ({phase})")
            state.update("phase", phase)
            time.sleep(3)
        
        # Reset to idle
        state.update("phase", "idle")
        
        print("\n🔄 System is running... Press Ctrl+C to stop")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 System stopped by user")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
        # Cleanup
        try:
            print("🧹 Cleaning up...")
            # Stop the lifespan
            if 'lifespan_context' in locals():
                loop.run_until_complete(lifespan_context.__aexit__(None, None, None))
            print("✅ Cleanup completed")
        except:
            pass

def run_simple_test():
    """Run a simple test of the display system"""
    print("🧪 Running Simple Display Test")
    print("=" * 40)
    
    try:
        from display.media_display import SimpleMediaDisplay
        from global_state import state
        
        # Initialize display
        display = SimpleMediaDisplay()
        if not display.display_initialized:
            print("❌ Display not initialized")
            return
        
        print("✅ Display initialized")
        
        # Start display
        display.start()
        
        # Test states
        print("🎮 Testing different states...")
        states = [
            (0, "Idle"),
            (1, "Processing"),
            (2, "Show Trash"),
            (3, "User Confirmation"),
            (4, "Success"),
            (6, "Reward")
        ]
        
        for state_num, state_name in states:
            print(f"📸 {state_name}")
            display.show_image(state_num)
            time.sleep(3)
        
        # Keep running
        print("\n🔄 Display running... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Test stopped by user")
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        if 'display' in locals():
            display.stop()

def main():
    """Main function"""
    print("🎯 iTrash System Test Options")
    print("=" * 40)
    print("1. Run complete unified system")
    print("2. Run simple display test")
    print("3. Exit")
    
    try:
        choice = input("\n🎯 Choose option (1-3): ").strip()
        
        if choice == "1":
            run_system()
        elif choice == "2":
            run_simple_test()
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 