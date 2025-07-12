# iTrash Unified System Setup Guide

This guide will help you set up and run the unified iTrash system that combines the SIRS and screen-itrash components.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp env.template .env
   # Edit .env with your actual values
   ```

3. **Run system checks:**
   ```bash
   python start.py --mode check
   ```

4. **Start the system:**
   ```bash
   python start.py --mode main
   ```

## 📋 Prerequisites

### Hardware Requirements
- Raspberry Pi (recommended) or Linux system
- WS2812B LED strip (60 LEDs)
- USB camera
- Proximity sensors (inductive sensors)
- GPIO pins for sensors

### Software Requirements
- Python 3.8+
- MongoDB database
- OpenAI API key
- YOLO API key (Roboflow)

### GPIO Pin Configuration
- **LED Strip**: GPIO 18
- **Object Detection Sensor**: GPIO 26
- **Blue Bin Sensor**: GPIO 19
- **Yellow Bin Sensor**: GPIO 12
- **Brown Bin Sensor**: GPIO 16

## 🔧 Installation Steps

### 1. Clone and Setup
```bash
cd iTrash
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp env.template .env
```

Edit `.env` file with your actual values:
```env
MONGO_CONNECTION_STRING=mongodb://your_mongodb_connection
MONGO_DB_NAME=itrash_db
OPENAI_API_KEY=your_openai_api_key
YOLO_API_KEY=your_yolo_api_key
```

### 3. Hardware Setup
1. Connect LED strip to GPIO 18
2. Connect proximity sensors to specified GPIO pins
3. Connect USB camera
4. Ensure proper power supply

### 4. Database Setup
1. Install MongoDB
2. Create database: `itrash_db`
3. Create collection: `acc`
4. Insert initial document: `{"acc": 0}`

## 🧪 Testing

### Test Individual Components
```bash
# Test database
python -c "from core.database import db_manager; print(db_manager.connect())"

# Test hardware (requires actual hardware)
python -c "from core.hardware import HardwareController; h = HardwareController()"

# Test camera
python -c "from core.camera import CameraController; c = CameraController(); print(c.initialize())"
```

## 🎮 Running the System

### Complete System
```bash
python main.py
```

### Analytics Dashboard
```bash
streamlit run analytics/dashboard.py
```

## 📊 System Architecture

```
iTrash/
├── main.py                 # Main application
├── requirements.txt       # Dependencies
├── env.template          # Environment template
├── config/
│   └── settings.py       # System configuration
├── core/
│   ├── hardware.py       # Hardware control
│   ├── camera.py         # Camera operations
│   ├── ai_classifier.py  # AI classification
│   └── database.py       # Database operations
├── display/
│   ├── media_display.py  # User interface
│   └── images/           # Display images
└── analytics/
    └── dashboard.py      # Analytics dashboard
```

## 🔄 System States

The system uses an accumulator (ACC) value to track states:

- **0**: Idle (white screen)
- **1**: Processing (processing screen)
- **2**: Show trash (show trash screen)
- **3**: User confirmation (try again screen)
- **4**: Success (great job screen)
- **5**: QR codes (QR codes screen)
- **6**: Reward (reward received screen)
- **7**: Incorrect (incorrect screen)
- **8**: Timeout (timeout screen)
- **9-11**: Throw instructions (throw screens)

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MongoDB is running
   - Verify connection string in `.env`
   - Ensure network connectivity

2. **Hardware Not Detected**
   - Check GPIO permissions
   - Verify pin connections
   - Run as root if needed: `sudo python main.py`

3. **Camera Not Working**
   - Check camera permissions
   - Verify USB connection
   - Test with: `python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`

4. **Display Not Showing**
   - Check X11 forwarding (if remote)
   - Verify image files exist
   - Check tkinter installation

5. **AI Classification Failing**
   - Verify API keys in `.env`
   - Check internet connectivity
   - Test API endpoints manually



## 📈 Analytics

### Access Dashboard
```bash
streamlit run analytics/dashboard.py
```

### Export Data
```python
from core.database import db_manager
db_manager.export_to_csv("data_export.csv")
```

## 🔒 Security Considerations

1. **API Keys**: Never commit `.env` file to version control
2. **Database**: Use strong passwords and network security
3. **Hardware**: Ensure physical security of the device
4. **Network**: Use VPN if accessing remotely

## 📝 Development

### Adding New Features
1. Create feature branch
2. Update documentation
3. Submit pull request

### Code Structure
- Follow PEP 8 style guide
- Add docstrings to all functions
- Use type hints where possible

## 🤝 Support

For issues and questions:
1. Check troubleshooting section
2. Run system tests
3. Check logs for error messages
4. Create issue with detailed description

## 📄 License

This project is licensed under the MIT License. 