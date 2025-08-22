## iTrash — Smart Trash Can System

An AI-driven smart trash can system that uses a camera, proximity sensors, LED strip, and a fullscreen display to detect, classify, and guide waste disposal. Includes a lightweight FastAPI server for monitoring that runs alongside the full system started by `main.py`.

### 🧭 Overview
iTrash solves the problem of improper waste sorting by guiding users to the correct bin with visual feedback and a simple display interface. The system integrates sensors, a USB camera, an addressable LED strip, a pygame-based display, and a FastAPI monitoring API. The project is stable and currently used in lab settings, with small improvements planned. It supports running the end-to-end hardware loop on a Raspberry Pi.

### ✨ Features
- **AI-powered classification**: Determines bin color (blue/yellow/brown) from the camera feed.
- **Proximity object detection**: Detects items and validates thrown bin using GPIO sensors.
- **LED step feedback**: Reflects state transitions (idle, processing, throw instructions, reward).
- **Fullscreen display guidance**: Pygame-driven image/video prompts for users.
- **Lightweight monitoring API**: FastAPI endpoints for latest classification and disposal events.

### 🧰 Requirements
- **Hardware**: Raspberry Pi 4, proximity sensors, USB camera, WS2813 LED strip, HDMI display.
- **Software**: Python 3.12+, FastAPI, uvicorn, OpenCV, pygame, and other dependencies in `requirements.txt`.

Important:
- WS281x/WS2813 LED control via `rpi-ws281x` is not currently compatible with Raspberry Pi 5. The underlying driver stack has not been updated; the LED strip will not work on Pi 5. Use a Raspberry Pi 4.

### 🚀 Quick Start
```bash
git clone <repo-url>
cd iTrash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start the system (hardware + display + API)
python main.py
```

### ⚙️ Configuration
iTrash reads configuration from environment variables via `python-dotenv`. Create a `.env` file in the project root or set environment variables directly. See `config/settings.py` for defaults.

```bash
# .env example

# AI/Model keys (optional — enable GPT/YOLO classification)
OPENAI_API_KEY=sk-xxxx
YOLO_API_KEY=rf-xxxx

# Classification defaults to GPT; YOLO keys are optional and disabled by default.
```

Key runtime settings are defined under:
- `config.settings.HardwareConfig` for LED strip, GPIO pins, and camera settings
- `config.settings.DisplayConfig` for image mapping and display
- `config.settings.TimingConfig` for delays between phases
- `config.settings.AIConfig` for model selection and prompts

### 🕹️ Usage
- **Run the system (Raspberry Pi)**: Connect sensors, LED strip, camera, and display. Then run:
  ```bash
  python main.py
  ```
  This starts the display, background hardware loop, and the monitoring API.

When `main.py` is running, the monitoring API is available at the configured host/port (default `http://localhost:8080`).

- **Example API calls**
  - Latest classification:
    ```bash
    curl http://localhost:8080/classification
    ```
  - Latest disposal event:
    ```bash
    curl http://localhost:8080/disposal
    ```



### 🗂️ Project Structure
```text
iTrash/
  main.py                 # Entry point: display + hardware loop + API
  global_state.py         # Shared thread-safe state singleton
  api/
    server.py             # FastAPI app (monitoring endpoints)
    state.py              # LocalState manager
  config/
    settings.py           # Hardware/Display/Timing/AI/API settings
  core/
    camera.py             # Camera controller
    hardware.py           # LED strip + GPIO proximity sensors
    ai_classifier.py      # GPT/YOLO classification manager
    hardware_loop.py      # Background loop driving sensors and phases
  display/
    media_display.py      # Fullscreen image/video display (pygame)
    images/               # UI assets for phases
    videos/               # Idle/intro video
```

### ✅ Results
- End-to-end flow validated on Raspberry Pi: detection → classification → guidance → reward.
- LED strip synchronized with display states for clear user feedback.
- Bin validation via proximity sensors with correct/incorrect handling and auto-reset.
- Monitoring API stable: latest classification and disposal history accessible.
- Stable in lab tests with continuous runtime and error recovery on display.

### 🗺️ Roadmap / Future Improvements
- Improve accuracy via model tuning and dataset expansion.
- Enhanced UI/UX on display and multilingual assets.
- MQTT telemetry and dashboard integration.

### 🤝 Contributing
Issues and pull requests are welcome. Use short, descriptive branches such as `feature/<name>` or `fix/<name>`. Please keep changes focused and include a brief test plan.

### 🪪 License
MIT License — see `LICENSE` if present, or include one in a new PR.

### 🙏 Acknowledgements
- IE Robotics & AI Lab
- Contributors and the open-source community
- Libraries: FastAPI, Uvicorn, OpenCV, Pygame, Roboflow Inference SDK


