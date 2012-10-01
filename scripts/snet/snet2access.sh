#!/bin/sh
# I start up the script that puts schoolnet data into the IEM Access database
# Started from cron @reboot invocation

# Make sure the PID exists before attempting to kill it!
if [ -e snet2access.pid ]; then
	kill -9 `cat snet2access.pid`	
fi
sleep 1
twistd --pidfile=snet2access.pid --logfile=/mesonet/data/logs/snet2access.log -y snet2access.py
# Wait a bit for twistd to fire up
sleep 10
# Allow nagios to monitor this file
chmod 644 snet2access.pid