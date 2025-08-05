#!/bin/bash

# iTrash Display Setup Script for Raspberry Pi
# This script helps set up proper display permissions before running the system

echo "🍓 iTrash Display Setup for Raspberry Pi"
echo "========================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  This script is designed for Raspberry Pi"
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run as root. Use a regular user account."
    exit 1
fi

# Set display environment
export DISPLAY=:0
export XAUTHORITY=$HOME/.Xauthority

echo "🔧 Setting up display environment..."
echo "   DISPLAY=$DISPLAY"
echo "   XAUTHORITY=$XAUTHORITY"

# Check if X11 is running
if ! pgrep -x "X" > /dev/null; then
    echo "⚠️  X11 server not detected. Make sure you're in a desktop environment."
    echo "   Try: startx or boot to desktop"
fi

# Check if we can access the display
if ! xset q > /dev/null 2>&1; then
    echo "⚠️  Cannot access display. Trying alternative setup..."
    
    # Try to get display from running processes
    DISPLAY_PID=$(pgrep -f "X.*:0" | head -1)
    if [ -n "$DISPLAY_PID" ]; then
        echo "   Found X11 process: $DISPLAY_PID"
    fi
fi

# Test Pygame display
echo "🎮 Testing Pygame display..."
python3 -c "
import pygame
import os
os.environ['SDL_VIDEODRIVER'] = 'x11'
os.environ['DISPLAY'] = ':0'
pygame.init()
try:
    info = pygame.display.Info()
    print(f'   ✅ Display detected: {info.current_w}x{info.current_h}')
    pygame.quit()
except Exception as e:
    print(f'   ❌ Display test failed: {e}')
"

echo ""
echo "🚀 Starting iTrash system..."

# Run the unified system
python3 unified_main.py 