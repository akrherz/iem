# This is the Twisted python process that collects schoolnet data
# Run via @reboot on mesonet's crontab

if [ -e mainserver.pid ]; then
	kill -9 `cat mainserver.pid `
	rm -f mainserver.pid
fi
twistd --pidfile=mainserver.pid --logfile=/mesonet/data/logs/mainserver.log -y mainserver.py
sleep 10
# Allow nagios to monitor
chmod 644 mainserver.pid
