#!/bin/sh

#cd /mesonet/scripts/snetPlex/bin


kill -9 `cat mainserver.pid `
twistd --pidfile=mainserver.pid --logfile=/mesonet/data/logs/mainserver.log -y mainserver.tac
chmod 644 mainserver.pid
