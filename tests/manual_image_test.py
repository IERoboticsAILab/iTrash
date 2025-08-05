#!/usr/bin/env python3
"""
Manual test script for iTrash image display system.
Allows interactive testing of different states and image display.
"""

import time
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from display.media_display import SimpleMediaDisplay
from config.settings import SystemStates, DisplayConfig
from global_state import state

def print_menu():
    """Print the test menu"""
    print("\n" + "=" * 60)
    print("🎮 iTrash Image Display Manual Test")
    print("=" * 60)
    print("Available states to test:")
    print("  0  - Idle (white.png)")
    print("  1  - Processing (processing_new.png)")
    print("  2  - Show Trash (show_trash.png)")
    print("  3  - User Confirmation (try_again_green.png)")
    print("  4  - Success (great_job.png)")
    print("  5  - QR Codes (qr_codes.png)")
    print("  6  - Reward (reward_received_new.png)")
    print("  7  - Incorrect (incorrect_new.png)")
    print("  8  - Timeout (timeout_new.png)")
    print("  9  - Throw Yellow (throw_yellow.png)")
    print("  10 - Throw Blue (throw_blue.png)")
    print("  11 - Throw Brown (throw_brown.png)")
    print("\nCommands:")
    print("  <number> - Show specific state")
    print("  'auto'   - Auto-cycle through all states")
    print("  'phase'  - Test phase-based state changes")
    print("  'status' - Show current status")
    print("  'quit'   - Exit test")
    print("=" * 60)

def auto_cycle(display):
    """Auto-cycle through all states"""
    print("\n🔄 Auto-cycling through all states...")
    
    for state_num in range(12):
        if state_num in DisplayConfig.IMAGE_MAPPING:
            image_file = DisplayConfig.IMAGE_MAPPING[state_num]
            print(f"\n📸 State {state_num}: {image_file}")
            
            success = display.show_image(state_num)
            if success:
                print(f"   ✅ Displayed: {display.current_image_path}")
            else:
                print(f"   ❌ Failed to display")
            
            time.sleep(3)  # Show each image for 3 seconds
    
    print("\n✅ Auto-cycle complete!")

def test_phase_changes(display):
    """Test phase-based state changes"""
    print("\n🔄 Testing phase-based state changes...")
    
    test_phases = [
        ("idle", "Idle"),
        ("processing", "Processing"),
        ("show_trash", "Show Trash"),
        ("user_confirmation", "User Confirmation"),
        ("idle", "Back to Idle")
    ]
    
    for phase, phase_name in test_phases:
        print(f"\n🔄 Changing to phase: {phase_name}")
        state.update("phase", phase)
        time.sleep(3)
    
    print("\n✅ Phase testing complete!")

def show_status(display):
    """Show current display status"""
    status = display.get_status()
    print(f"\n📊 Current Status:")
    print(f"   State: {status['acc']}")
    print(f"   Current Image: {status['current_image']}")
    print(f"   System Running: {status['is_running']}")
    
    # Show current phase
    current_phase = state.get("phase", "unknown")
    print(f"   Current Phase: {current_phase}")

def main():
    """Main manual test function"""
    
    print("🚀 Starting iTrash Image Display Manual Test")
    
    # Initialize display
    try:
        display = SimpleMediaDisplay()
        print("✅ Display system initialized")
    except Exception as e:
        print(f"❌ Failed to initialize display: {e}")
        return
    
    # Check images directory
    images_dir = Path("display/images")
    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return
    
    print(f"✅ Images directory found: {images_dir}")
    
    # Show initial state
    display.show_image(SystemStates.IDLE)
    print(f"📸 Initial state displayed: {display.current_image_path}")
    
    # Main test loop
    while True:
        print_menu()
        
        try:
            command = input("\n🎯 Enter command: ").strip().lower()
            
            if command == 'quit':
                print("👋 Goodbye!")
                break
            
            elif command == 'auto':
                auto_cycle(display)
            
            elif command == 'phase':
                test_phase_changes(display)
            
            elif command == 'status':
                show_status(display)
            
            elif command.isdigit():
                state_num = int(command)
                if 0 <= state_num <= 11:
                    if state_num in DisplayConfig.IMAGE_MAPPING:
                        image_file = DisplayConfig.IMAGE_MAPPING[state_num]
                        print(f"\n📸 Showing state {state_num}: {image_file}")
                        
                        success = display.show_image(state_num)
                        if success:
                            print(f"   ✅ Displayed: {display.current_image_path}")
                        else:
                            print(f"   ❌ Failed to display")
                    else:
                        print(f"❌ No image mapping for state {state_num}")
                else:
                    print(f"❌ Invalid state number: {state_num}")
            
            else:
                print(f"❌ Unknown command: {command}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Test interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Cleanup
    try:
        display.stop()
        print("✅ Display system stopped")
    except:
        pass

if __name__ == "__main__":
    main() 