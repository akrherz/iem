#!/bin/sh

#cd /mesonet/scripts/snetPlex/bin

export PATH=/mesonet/python-2.5/bin:$PATH

which twistd
kill -9 `cat mainserver.pid `
twistd --pidfile=mainserver.pid --logfile=/mesonet/data/logs/mainserver.log -y mainserver.tac
chmod 644 mainserver.pid
