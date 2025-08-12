"""
Lightweight API server exposing system state for monitoring.

Endpoints:
- GET /classification/latest: returns the most recent classification and current phase
"""

from fastapi import FastAPI
import threading
from typing import Optional

from global_state import state
from config.settings import APIConfig

app = FastAPI(title="iTrash API", version="1.0.0")


@app.get("/classification")
def get_latest_classification():
    last = state.get("last_classification")
    return {
        "id": "",  # reserved
        "last_classification" : last if last != "" else "error",
        "timestamp": state.get("last_classification_ts"),
    }


@app.get("/disposal")
def get_latest_disposal():
    disp = state.get("last_disposal") or {}
    return {
        "id": "",  # reserved
        "user_thrown": disp.get("user_thrown"),
        "timestamp": disp.get("timestamp"),
        "correct": disp.get("correct"),
    }


def start_api_server() -> Optional[threading.Thread]:
    """Start the API server in a background thread.

    Returns the thread object if started; otherwise None.
    """
    try:
        import uvicorn

        def run_server():
            uvicorn.run(
                app,
                host=APIConfig.HOST,
                port=APIConfig.PORT,
                log_level="warning",
            )

        api_thread = threading.Thread(target=run_server, daemon=True)
        api_thread.start()
        return api_thread
    except Exception:
        return None


