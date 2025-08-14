"""
Simple LED strip test for iTrash.

This script cycles the LED strip through a few basic colors,
performs a short flash sequence, and then clears the strip.

Run from the project root:
    python core/test_led_strip.py
"""

import sys
import time
from pathlib import Path


# Ensure project root is on sys.path when running directly
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _import_hardware_modules():
    """Import hardware modules with a clear error if running off-RPi."""
    try:
        from core.hardware import LEDStrip
        from config.settings import Colors
        return LEDStrip, Colors
    except Exception as import_error:
        print("Failed to import hardware modules. This script must run on the Raspberry Pi with required libraries installed.")
        print(f"Error: {import_error}")
        sys.exit(1)


def cycle_basic_colors(led_strip, delay_seconds: float = 0.5, iterations: int = 1) -> None:
    """Cycle through a set of basic colors on the LED strip.

    Args:
        led_strip: Instance of LEDStrip
        delay_seconds: Delay between color changes
        iterations: Number of full cycles to run
    """
    from config.settings import Colors

    color_sequence = [
        Colors.RED,
        Colors.GREEN,
        Colors.BLUE,
        Colors.YELLOW,
        Colors.WHITE,
        Colors.BROWN,
        Colors.EMPTY,
    ]

    for _ in range(iterations):
        for rgb_color in color_sequence:
            led_strip.set_color_all(rgb_color)
            time.sleep(delay_seconds)


def flash_sequence(led_strip, flashes: int = 3, wait_ms: int = 150) -> None:
    """Flash the LED strip a few times as a quick test effect."""
    from config.settings import Colors

    for _ in range(flashes):
        led_strip.flash(Colors.GREEN, wait_ms=wait_ms)


def main() -> None:
    LEDStrip, Colors = _import_hardware_modules()

    led_strip = None
    try:
        print("Initializing LED strip...")
        led_strip = LEDStrip()

        print("Cycling basic colors...")
        cycle_basic_colors(led_strip, delay_seconds=0.5, iterations=2)

        print("Running flash sequence...")
        flash_sequence(led_strip, flashes=3, wait_ms=150)

        print("Clearing LEDs...")
        led_strip.clear_all()
        print("LED strip test complete.")

    except KeyboardInterrupt:
        print("\nInterrupted by user. Clearing LEDs and exiting...")
        if led_strip is not None:
            led_strip.clear_all()
    except Exception as unexpected_error:
        print(f"Unexpected error: {unexpected_error}")
        if led_strip is not None:
            led_strip.clear_all()
        raise


if __name__ == "__main__":
    main()


