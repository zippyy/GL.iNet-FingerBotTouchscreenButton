#!/bin/sh
set -eu

if [ -x /etc/init.d/S99fingerbot-touch ]; then
    /etc/init.d/S99fingerbot-touch stop || true
fi

rm -f /etc/rcS.d/S99fingerbot-touch
rm -f /etc/init.d/S99fingerbot-touch
rm -f /usr/sbin/fingerbot-touch.py
rm -f /var/run/fingerbot-touch.pid

echo "FingerBot touch daemon removed."
echo "Backup files under /userdata/custom/fingerbot were preserved."
