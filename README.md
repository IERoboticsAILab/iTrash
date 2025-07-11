# iTrash - Unified Smart Waste Management System

A comprehensive smart waste management system that combines hardware control, AI-powered trash classification, user interface display, and analytics capabilities.

## Features

### 🏗️ Hardware Integration
- **LED Strip Control**: WS2812B LED strip for visual feedback
- **Proximity Sensors**: Inductive sensors for object detection
- **Camera Integration**: Real-time trash classification
- **QR Code Detection**: User identification and wallet integration

### 🤖 AI-Powered Classification
- **YOLO Model**: Real-time object detection and classification
- **GPT-4 Vision**: Advanced image analysis for trash categorization
- **Multi-class Support**: Blue (cardboard/paper), Yellow (plastic/metal), Brown (organic)

### 🖥️ User Interface
- **Full-screen Display**: Tkinter-based interface with image transitions
- **Browser Integration**: Chromium window management
- **Visual Feedback**: Dynamic image display based on system state
- **State Management**: MongoDB-based accumulator system

### 📊 Analytics & Data Management
- **Data Collection**: Image storage with metadata
- **Analytics Dashboard**: Streamlit-based analytics interface
- **Performance Tracking**: Usage statistics and classification accuracy
- **Export Capabilities**: CSV and visualization exports

## System Architecture

```
iTrash/
├── core/                 # Core system components
│   ├── hardware.py      # Hardware control (LEDs, sensors)
│   ├── camera.py        # Camera and image processing
│   ├── ai_classifier.py # AI classification models
│   └── database.py      # Database operations
├── display/             # User interface components
│   ├── media_display.py # Main display interface
│   └── images/          # Display images
├── analytics/           # Data analysis tools
│   ├── dashboard.py     # Streamlit analytics dashboard
│   └── utils.py         # Analytics utilities
├── config/              # Configuration files
│   └── settings.py      # System settings
└── main.py              # Main application entry point
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd iTrash
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file with:
   ```
   MONGO_CONNECTION_STRING=your_mongodb_connection_string
   MONGO_DB_NAME=your_database_name
   OPENAI_API_KEY=your_openai_api_key
   YOLO_API_KEY=your_yolo_api_key
   ```

4. **Hardware Setup**:
   - Connect WS2812B LED strip to GPIO 18
   - Connect proximity sensors to GPIO pins 26, 19, 12, 16
   - Connect camera to USB port

## Usage

### Running the Main System
```bash
python main.py
```

### Running Analytics Dashboard
```bash
streamlit run analytics/dashboard.py
```

### Running Display Interface Only
```bash
python display/media_display.py
```

## Configuration

### Hardware Pins
- **LED Strip**: GPIO 18
- **Object Detection Sensor**: GPIO 26
- **Blue Bin Sensor**: GPIO 19
- **Yellow Bin Sensor**: GPIO 12
- **Brown Bin Sensor**: GPIO 16

### System States (ACC Values)
- **0**: Idle/White screen
- **1**: Processing/Processing screen
- **2**: Show trash/Show trash screen
- **3**: User confirmation/Try again screen
- **4**: Success/Great job screen
- **5**: QR codes/QR codes screen
- **6**: Reward/Reward received screen

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 