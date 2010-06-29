#!/bin/sh
# I run from rc.local and mine the realtime feed of data into iemaccess

export PYTHONPATH=$PYTHONPATH:/mesonet/scripts/snetPlex
export PATH=/mesonet/python-2.5/bin:$PATH

kill -9 `cat twistd.pid`
sleep 1
twistd --logfile=/mesonet/data/logs/s2i.log -y s2i.tac
