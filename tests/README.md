# iTrash System Tests

This directory contains comprehensive tests for the iTrash system with fullscreen display integration.

## 🧪 Test Files

### **Core System Tests**

#### `test_complete_system.py`
**Comprehensive end-to-end system test**
- Tests display integration with the complete system
- Verifies state management and hardware loop integration
- Tests error handling and recovery
- Simulates complete trash disposal cycles
- **Usage**: `python tests/test_complete_system.py`

#### `run_system_test.py`
**Run the actual iTrash system**
- Option 1: Run complete unified system (FastAPI + Display + Hardware Loop)
- Option 2: Run simple display test
- Tests the real system, not just components
- **Usage**: `python tests/run_system_test.py`

### **Display System Tests**

#### `test_updated_display.py`
**Test the updated fullscreen display system**
- Tests display initialization and image loading
- Verifies state cycling and image switching
- Tests the DisplayManager class
- **Usage**: `python tests/test_updated_display.py`

#### `test_image_display.py`
**Basic image display functionality test**
- Tests image file access and loading
- Verifies image mapping configuration
- Tests basic display functionality
- **Usage**: `python tests/test_image_display.py`

### **Fullscreen Display Tests**

#### `fullscreen_image_test.py`
**Test different fullscreen display methods**
- Tests PIL + Tkinter fullscreen
- Tests OpenCV fullscreen
- Tests SDL/Pygame fullscreen
- Compares different methods for best performance
- **Usage**: `python tests/fullscreen_image_test.py`

#### `basic_image_display_test.py`
**Test basic image display with multiple methods**
- Tests PIL, OpenCV, Matplotlib, and system default viewers
- Helps identify which display method works best
- **Usage**: `python tests/basic_image_display_test.py`

#### `manual_image_test.py`
**Interactive manual testing**
- Allows manual testing of different states
- Interactive menu for testing specific images
- Auto-cycling through all states
- **Usage**: `python tests/manual_image_test.py`

## 🚀 Quick Start

### **Test the Complete System**
```bash
python tests/test_complete_system.py
```

### **Run the Actual System**
```bash
python tests/run_system_test.py
```

### **Test Display Only**
```bash
python tests/test_updated_display.py
```

## 🎯 What Each Test Verifies

### **System Integration**
- ✅ Display system integrates with global state
- ✅ Hardware loop communicates with display
- ✅ FastAPI application works with display
- ✅ State changes trigger correct image displays

### **Display Functionality**
- ✅ Fullscreen display without window decorations
- ✅ Images scale properly and maintain aspect ratio
- ✅ Black background fills empty space
- ✅ Smooth transitions between states
- ✅ All 12 system states display correct images

### **Error Handling**
- ✅ Invalid states are handled gracefully
- ✅ Missing images don't crash the system
- ✅ Display errors are caught and reported
- ✅ System recovers from errors

## 📋 Test Results

When tests pass, you should see:
- **Fullscreen images** without borders or decorations
- **Smooth state transitions** as the system changes phases
- **Proper image scaling** that maintains aspect ratio
- **Black backgrounds** around images for clean appearance
- **All states working** (idle, processing, show_trash, etc.)

## 🛠️ Troubleshooting

### **Display Not Working**
1. Check if Pygame is installed: `pip install pygame`
2. Verify you have a display environment available
3. Check that images exist in `display/images/` directory

### **Tests Failing**
1. Check the error messages for specific issues
2. Verify all dependencies are installed
3. Make sure the system is not already running

### **Performance Issues**
1. Try different display methods in `fullscreen_image_test.py`
2. Check if your system supports hardware acceleration
3. Verify screen resolution settings

## 🎉 Success Indicators

When everything is working correctly:
- ✅ All tests pass
- ✅ Images display in true fullscreen
- ✅ State changes trigger image updates
- ✅ System runs without errors
- ✅ Display responds to hardware events

Your iTrash system is ready for production use! 