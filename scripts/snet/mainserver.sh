#!/bin/sh

kill -9 `cat mainserver.pid `
twistd --pidfile=mainserver.pid --logfile=/mesonet/data/logs/mainserver.log -y mainserver.py
# Allow nagios to monitor
chmod 644 mainserver.pid
