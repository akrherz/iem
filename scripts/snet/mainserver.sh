# This is the Twisted python process that collects schoolnet data
# Run via @reboot on mesonet's crontab

if [ -e mainserver.pid ]; then
	kill -9 `cat mainserver.pid `
	rm -f mainserver.pid
fi
# For some reason, this file 'corrupts' at reboot and sometimes is 000 perms
# delete it each time, otherwise mainserver won't start!
rm -f /mesonet/data/logs/mainserver.log
twistd --pidfile=mainserver.pid --logfile=/mesonet/data/logs/mainserver.log -y mainserver.py
sleep 10
# Allow nagios to monitor
chmod 644 mainserver.pid
