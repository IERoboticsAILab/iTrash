"""
Lightweight API server exposing system state for monitoring.

Endpoints:
- GET /classification/latest: returns the most recent classification and current phase
"""

from fastapi import FastAPI
import threading
from typing import Optional
import logging

from global_state import state
from config.settings import APIConfig

app = FastAPI(title="iTrash API", version="1.0.0")
logger = logging.getLogger(__name__)


@app.get("/classification")
def get_latest_classification():
    last = state.get("last_classification")
    return {
        "id": "",  # reserved
        "last_classification": last if last not in (None, "") else "error",
        "timestamp": state.get("last_classification_ts"),
    }


@app.get("/disposal")
def get_latest_disposal():
    disp = state.get("last_disposal") or {}
    return {
        "id": "",  # reserved
        "user_thrown": disp.get("user_thrown") if disp.get("user_thrown") not in (None, "") else "error",
        "timestamp": disp.get("timestamp"),
        "correct": disp.get("correct") if disp.get("correct") is not None else "error",
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
    except Exception as e:
        logger.warning("API server could not be started: %s", e)
        return None


