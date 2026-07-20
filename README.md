# GL.iNet FingerBot Touchscreen Button

Adds a persistent touchscreen activation region to a GL.iNet Comet Pro / GL-RM10. Touching the configured lower-screen region runs the built-in FingerBot command.

## Tested platform

- GL.iNet Comet Pro / GL-RM10
- Buildroot 2024.02
- Firmware `rm10-1.10.0-beta1`
- Touch controller `SPD2010`
- Touch input normally `/dev/input/event0`

## What it does

The daemon reads Linux input events directly from the touchscreen and watches this region:

```text
X: 15–165
Y: 380–445
```

When touched, it executes:

```sh
/usr/sbin/fingerbot set-action 800 500 803
```

It does not write to `/dev/fb0`, modify the LVGL application, or draw anything on screen. Add a visual button to the custom background separately.

## Install

SSH into the Comet, clone the repository, and run:

```sh
git clone https://github.com/zippyy/GL.iNet-FingerBotTouchscreenButton.git
cd GL.iNet-FingerBotTouchscreenButton
chmod +x scripts/install.sh
./scripts/install.sh
```

If `git` is unavailable on the Comet, copy the repository to the device with `scp` and run the same installer.

## Service commands

```sh
/etc/init.d/S99fingerbot-touch start
/etc/init.d/S99fingerbot-touch stop
/etc/init.d/S99fingerbot-touch restart
/etc/init.d/S99fingerbot-touch status
```

View the log:

```sh
tail -f /var/log/fingerbot-touch.log
```

## Reboot persistence

The installer places the executable init script at:

```text
/etc/init.d/S99fingerbot-touch
```

On firmware using `/etc/rcS.d`, it also creates:

```text
/etc/rcS.d/S99fingerbot-touch
```

Backup copies are stored at:

```text
/userdata/custom/fingerbot/
```

Normal reboots should preserve the installation. Firmware upgrades or factory resets may remove overlay changes.

## Configuration

Edit these values in `src/fingerbot-touch.py` before installing:

```python
X_MIN, X_MAX = 15, 165
Y_MIN, Y_MAX = 380, 445

PUSH_TIME = 800
HOLD_TIME = 500
PULL_TIME = 803
```

After changing the installed copy:

```sh
/etc/init.d/S99fingerbot-touch restart
```

## Troubleshooting

Verify that the built-in command works:

```sh
/usr/sbin/fingerbot set-action 800 500 803
```

List input devices:

```sh
for d in /dev/input/event*; do
    echo "===== $d ====="
    cat "/sys/class/input/$(basename "$d")/device/name" 2>/dev/null
done
```

The tested touchscreen reports:

```text
SPD2010
```

Check daemon output:

```sh
cat /var/log/fingerbot-touch.log
```

## Uninstall

```sh
chmod +x scripts/uninstall.sh
./scripts/uninstall.sh
```

## License

MIT
