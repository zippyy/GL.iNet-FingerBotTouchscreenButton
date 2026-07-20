#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

cp "$SCRIPT_DIR/src/fingerbot-touch.py" /usr/sbin/fingerbot-touch.py
chmod 0755 /usr/sbin/fingerbot-touch.py

cp "$SCRIPT_DIR/init/S99fingerbot-touch" /etc/init.d/S99fingerbot-touch
chmod 0755 /etc/init.d/S99fingerbot-touch

mkdir -p /userdata/custom/fingerbot
cp /usr/sbin/fingerbot-touch.py /userdata/custom/fingerbot/fingerbot-touch.py
cp /etc/init.d/S99fingerbot-touch /userdata/custom/fingerbot/S99fingerbot-touch

if [ -d /etc/rcS.d ]; then
    ln -sf /etc/init.d/S99fingerbot-touch /etc/rcS.d/S99fingerbot-touch
fi

/etc/init.d/S99fingerbot-touch restart

echo
/etc/init.d/S99fingerbot-touch status
echo
echo "Log: /var/log/fingerbot-touch.log"
