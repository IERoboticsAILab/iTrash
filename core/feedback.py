"""
LED feedback helpers for iTrash runtime states.
"""

import time
from typing import Callable, Optional

from config.settings import Colors, SystemStates


STATE_LED_COLORS = {
    SystemStates.IDLE: Colors.EMPTY,
    SystemStates.PROCESSING: Colors.WHITE,
    SystemStates.SHOW_TRASH: Colors.WHITE,
    SystemStates.USER_CONFIRMATION: Colors.RED,
    SystemStates.SUCCESS: Colors.GREEN,
    SystemStates.QR_CODES: Colors.GREEN,
    SystemStates.REWARD: Colors.GREEN,
    SystemStates.INCORRECT: Colors.RED,
    SystemStates.TIMEOUT: Colors.RED,
    SystemStates.THROW_YELLOW: Colors.YELLOW,
    SystemStates.THROW_BLUE: Colors.BLUE,
    SystemStates.THROW_BROWN: Colors.BROWN,
}


class LEDFeedback:
    """Small wrapper around the LED strip for consistent feedback behavior."""

    def __init__(self, led_strip):
        self.led_strip = led_strip

    def set_color(self, color):
        if not self.led_strip:
            return
        if color == Colors.EMPTY:
            self.clear()
            return
        self.led_strip.clear_all()
        self.led_strip.set_color_all(color)

    def clear(self):
        if not self.led_strip:
            return
        self.led_strip.clear_all()
        time.sleep(0.01)
        self.led_strip.clear_all()

    def set_state(self, state_value):
        self.set_color(STATE_LED_COLORS.get(state_value, Colors.EMPTY))

    def blink(
        self,
        color,
        cycles: int,
        on_seconds: float,
        off_seconds: float,
        on_started: Optional[Callable[[], None]] = None,
    ):
        if not self.led_strip:
            if on_started is not None:
                on_started()
            for _ in range(cycles):
                time.sleep(on_seconds)
                time.sleep(off_seconds)
            return
        for cycle_index in range(cycles):
            self.led_strip.set_color_all(color)
            if cycle_index == 0 and on_started is not None:
                on_started()
            time.sleep(on_seconds)
            self.led_strip.clear_all()
            time.sleep(off_seconds)

    def blink_capture_countdown(self, on_started: Optional[Callable[[], None]] = None):
        self.blink(
            Colors.WHITE,
            cycles=4,
            on_seconds=0.125,
            off_seconds=0.125,
            on_started=on_started,
        )
