#!/usr/bin/env python3
"""Touch-region daemon for controlling a FingerBot from a GL.iNet Comet."""

import glob
import os
import select
import struct
import subprocess
import time

# Touch coordinates on the Comet Pro / GL-RM10 portrait display.
X_MIN, X_MAX = 15, 165
Y_MIN, Y_MAX = 380, 445

# FingerBot timing arguments, in milliseconds.
PUSH_TIME = 800
HOLD_TIME = 500
PULL_TIME = 803

EV_SYN = 0x00
EV_KEY = 0x01
EV_ABS = 0x03

SYN_REPORT = 0
BTN_TOUCH = 330
ABS_X = 0
ABS_Y = 1
ABS_MT_POSITION_X = 53
ABS_MT_POSITION_Y = 54
ABS_MT_TRACKING_ID = 57

EVENT = struct.Struct("llHHi")
MIN_TRIGGER_INTERVAL = 1.0


def find_touch_device():
    """Locate the touchscreen, preferring the known SPD2010 controller."""
    candidates = []

    for device in sorted(glob.glob("/dev/input/event*")):
        event_name = os.path.basename(device)
        name_path = f"/sys/class/input/{event_name}/device/name"

        try:
            with open(name_path, "r", encoding="utf-8") as file:
                name = file.read().strip()
        except OSError:
            name = ""

        print(f"Input candidate: {device} [{name}]", flush=True)
        lowered = name.lower()

        if name == "SPD2010":
            return device

        if any(word in lowered for word in (
            "touch",
            "touchscreen",
            "goodix",
            "focal",
            "ft5",
            "gt9",
        )):
            return device

        candidates.append(device)

    if "/dev/input/event0" in candidates:
        return "/dev/input/event0"

    return candidates[0] if candidates else None


def activate(x, y):
    """Run the GL.iNet FingerBot command."""
    print(f"FingerBot activated at x={x}, y={y}", flush=True)

    result = subprocess.run(
        [
            "/usr/sbin/fingerbot",
            "set-action",
            str(PUSH_TIME),
            str(HOLD_TIME),
            str(PULL_TIME),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout.strip(), flush=True)

    print(f"fingerbot exit code: {result.returncode}", flush=True)


def run():
    while True:
        device = find_touch_device()

        if not device:
            print("No input devices found; retrying in 2 seconds", flush=True)
            time.sleep(2)
            continue

        x = None
        y = None
        pressed = False
        fired = False
        last_fire = 0.0

        try:
            print(f"Opening touchscreen: {device}", flush=True)

            with open(device, "rb", buffering=0) as dev:
                while True:
                    readable, _, _ = select.select([dev], [], [], 5)

                    if not readable:
                        continue

                    data = dev.read(EVENT.size)

                    if len(data) != EVENT.size:
                        raise RuntimeError("Short read from input device")

                    _, _, event_type, code, value = EVENT.unpack(data)

                    if event_type == EV_ABS:
                        if code in (ABS_X, ABS_MT_POSITION_X):
                            x = value
                        elif code in (ABS_Y, ABS_MT_POSITION_Y):
                            y = value
                        elif code == ABS_MT_TRACKING_ID:
                            pressed = value >= 0
                            fired = False

                    elif event_type == EV_KEY and code == BTN_TOUCH:
                        pressed = value != 0
                        if pressed:
                            fired = False

                    elif event_type == EV_SYN and code == SYN_REPORT:
                        inside = (
                            x is not None
                            and y is not None
                            and X_MIN <= x <= X_MAX
                            and Y_MIN <= y <= Y_MAX
                        )

                        if pressed and inside and not fired:
                            now = time.monotonic()

                            if now - last_fire >= MIN_TRIGGER_INTERVAL:
                                fired = True
                                last_fire = now
                                activate(x, y)

        except Exception as error:
            print(
                f"Input device error on {device}: {error}; "
                "rescanning in 2 seconds",
                flush=True,
            )
            time.sleep(2)


if __name__ == "__main__":
    run()
