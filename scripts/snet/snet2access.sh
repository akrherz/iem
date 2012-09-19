#!/bin/sh
# I start up the script that puts schoolnet data into the IEM Access database
# Started from cron @reboot invocation

kill -9 `cat snet2access.pid`
sleep 1
twistd --pidfile=snet2access.pid --logfile=/mesonet/data/logs/snet2access.log -y snet2access.py
# Allow nagios to monitor this file
chmod 644 snet2access.pid