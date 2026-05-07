import asyncio
import sys
import types
import unittest
from unittest.mock import patch

import numpy as np


gpio_stub = types.ModuleType("RPi.GPIO")
gpio_stub.BCM = "BCM"
gpio_stub.IN = "IN"
gpio_stub.PUD_DOWN = "PUD_DOWN"
gpio_stub.setmode = lambda *args, **kwargs: None
gpio_stub.setup = lambda *args, **kwargs: None
gpio_stub.input = lambda *args, **kwargs: 1
gpio_stub.cleanup = lambda *args, **kwargs: None
rpi_stub = types.ModuleType("RPi")
rpi_stub.GPIO = gpio_stub
sys.modules.setdefault("RPi", rpi_stub)
sys.modules.setdefault("RPi.GPIO", gpio_stub)

ws_stub = types.ModuleType("rpi_ws281x")
ws_stub.Color = lambda r, g, b: (r, g, b)
ws_stub.Adafruit_NeoPixel = object
sys.modules.setdefault("rpi_ws281x", ws_stub)

inference_sdk_stub = types.ModuleType("inference_sdk")
inference_sdk_stub.InferenceHTTPClient = object
sys.modules.setdefault("inference_sdk", inference_sdk_stub)

from core.hardware_loop import HardwareLoop
from global_state import state


class FakeLEDStrip:
    def __init__(self):
        self.events = []

    def set_color_all(self, color):
        self.events.append(("set", color))

    def clear_all(self):
        self.events.append(("clear", None))


class FakeHardware:
    def __init__(self, led_strip):
        self.led_strip = led_strip

    def get_led_strip(self):
        return self.led_strip


class FakeCamera:
    def __init__(self, frame):
        self.frame = frame
        self.flush_count = 0
        self.capture_count = 0

    def flush_stale_frames(self):
        self.flush_count += 1

    def capture_for_classification(self):
        self.capture_count += 1
        return self.frame


class FakeClassifier:
    def __init__(self, result):
        self.result = result
        self.images = []

    async def process_image_with_feedback(self, image):
        self.images.append(image)
        return self.result


def make_loop(camera, classifier, led_strip):
    loop = HardwareLoop.__new__(HardwareLoop)
    loop.is_running = True
    loop.thread = None
    loop.hardware = FakeHardware(led_strip)
    loop.camera = camera
    loop.classifier = classifier
    return loop


class HardwareLoopCaptureTest(unittest.TestCase):
    def setUp(self):
        state.reset()

    def test_prepare_capture_flushes_camera_and_blinks_white_before_capture(self):
        frame = np.zeros((4, 4, 3), dtype=np.uint8)
        led_strip = FakeLEDStrip()
        camera = FakeCamera(frame)
        classifier = FakeClassifier("blue")
        loop = make_loop(camera, classifier, led_strip)

        with patch("core.feedback.time.sleep") as sleep:
            captured = loop._prepare_capture()

        self.assertIs(captured, frame)
        self.assertEqual(camera.flush_count, 1)
        self.assertEqual(camera.capture_count, 1)
        self.assertEqual(led_strip.events.count(("set", (255, 255, 255))), 4)
        self.assertEqual(led_strip.events.count(("clear", None)), 4)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.125] * 8)

    def test_prepare_capture_still_flushes_and_waits_without_led_strip(self):
        frame = np.zeros((4, 4, 3), dtype=np.uint8)
        camera = FakeCamera(frame)
        classifier = FakeClassifier("blue")
        loop = make_loop(camera, classifier, led_strip=None)

        with patch("core.feedback.time.sleep") as sleep:
            captured = loop._prepare_capture()

        self.assertIs(captured, frame)
        self.assertEqual(camera.flush_count, 1)
        self.assertEqual(camera.capture_count, 1)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [0.125] * 8)

    def test_classification_result_still_moves_to_matching_trash_phase(self):
        frame = np.zeros((4, 4, 3), dtype=np.uint8)
        led_strip = FakeLEDStrip()
        camera = FakeCamera(frame)
        classifier = FakeClassifier("yellow")
        loop = make_loop(camera, classifier, led_strip)

        with (
            patch.object(loop, "_prepare_capture", return_value=frame),
            patch("core.hardware_loop.threading.Thread") as thread_cls,
            patch("core.hardware_loop.time.sleep"),
        ):
            def run_immediately(target, daemon):
                class ImmediateThread:
                    def start(self):
                        target()

                    def join(self, timeout=None):
                        return None

                    def is_alive(self):
                        return False

                return ImmediateThread()

            thread_cls.side_effect = run_immediately
            loop._process_trash_detection()

        self.assertEqual(state.get("last_classification"), "yellow")
        self.assertEqual(state.get("phase"), "yellow_trash")
        self.assertEqual(classifier.images, [frame])

    def test_camera_failure_moves_to_error_phase(self):
        led_strip = FakeLEDStrip()
        camera = FakeCamera(None)
        classifier = FakeClassifier("blue")
        loop = make_loop(camera, classifier, led_strip)

        with patch.object(loop, "_prepare_capture", return_value=None):
            loop._process_trash_detection()

        self.assertEqual(state.get("phase"), "error")


if __name__ == "__main__":
    unittest.main()
