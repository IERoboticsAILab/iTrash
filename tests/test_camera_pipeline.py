import unittest
from unittest.mock import patch

import numpy as np

from core.camera import CameraController


class FakeCapture:
    def __init__(self, frames):
        self.frames = list(frames)
        self.read_count = 0

    def read(self):
        self.read_count += 1
        if not self.frames:
            return False, None
        return True, self.frames.pop(0)


class CameraPipelineTest(unittest.TestCase):
    def test_flush_reads_configured_stale_frames_before_final_capture(self):
        stale_frames = [np.full((4, 4, 3), i, dtype=np.uint8) for i in range(5)]
        final_frame = np.full((4, 4, 3), 99, dtype=np.uint8)
        camera = CameraController()
        camera.cap = FakeCapture(stale_frames + [final_frame])
        camera.is_initialized = True

        with (
            patch("core.camera.HardwareConfig.STALE_FRAME_FLUSH_COUNT", 5),
            patch("core.camera.HardwareConfig.CAPTURE_DEBUG_SAVE_ENABLED", False),
            patch("core.camera.HardwareConfig.CLASSIFIER_IMAGE_LONG_EDGE", 4),
        ):
            camera.flush_stale_frames()
            captured = camera.capture_for_classification()

        self.assertEqual(camera.cap.read_count, 6)
        np.testing.assert_array_equal(captured, final_frame)

    def test_debug_saving_disabled_does_not_write_captured_image(self):
        frame = np.full((4, 4, 3), 7, dtype=np.uint8)
        camera = CameraController()
        camera.cap = FakeCapture([frame])
        camera.is_initialized = True

        with (
            patch("core.camera.HardwareConfig.CAPTURE_DEBUG_SAVE_ENABLED", False),
            patch("core.camera.HardwareConfig.CLASSIFIER_IMAGE_LONG_EDGE", 4),
            patch("core.camera.cv2.imwrite") as imwrite,
        ):
            captured = camera.capture_for_classification()

        np.testing.assert_array_equal(captured, frame)
        imwrite.assert_not_called()

    def test_debug_saving_enabled_writes_one_raw_capture(self):
        frame = np.full((4, 4, 3), 7, dtype=np.uint8)
        camera = CameraController()
        camera.cap = FakeCapture([frame])
        camera.is_initialized = True

        with (
            patch("core.camera.HardwareConfig.CAPTURE_DEBUG_SAVE_ENABLED", True),
            patch("core.camera.HardwareConfig.CLASSIFIER_IMAGE_LONG_EDGE", 4),
            patch("core.camera.os.makedirs"),
            patch("core.camera.cv2.imwrite", return_value=True) as imwrite,
        ):
            captured = camera.capture_for_classification()

        np.testing.assert_array_equal(captured, frame)
        imwrite.assert_called_once()

    def test_disabled_crop_returns_full_frame(self):
        frame = np.arange(4 * 5 * 3, dtype=np.uint8).reshape((4, 5, 3))

        with patch("core.camera.HardwareConfig.CROP_ENABLED", False):
            cropped = CameraController.apply_configured_crop(frame)

        np.testing.assert_array_equal(cropped, frame)

    def test_enabled_crop_returns_configured_region(self):
        frame = np.arange(6 * 8 * 3, dtype=np.uint8).reshape((6, 8, 3))

        with (
            patch("core.camera.HardwareConfig.CROP_ENABLED", True),
            patch("core.camera.HardwareConfig.CROP_X", 2),
            patch("core.camera.HardwareConfig.CROP_Y", 1),
            patch("core.camera.HardwareConfig.CROP_WIDTH", 3),
            patch("core.camera.HardwareConfig.CROP_HEIGHT", 4),
        ):
            cropped = CameraController.apply_configured_crop(frame)

        np.testing.assert_array_equal(cropped, frame[1:5, 2:5])


if __name__ == "__main__":
    unittest.main()
