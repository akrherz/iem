#!/bin/sh

#export PYTHONPATH=$PYTHONPATH:/home/nafai/Twisted-1.0.7alpha4
#export PATH=$PATH:/home/nafai/Twisted-1.0.7alpha4/bin

kill -9 `cat twistd.pid`
sleep 1
mv twistd.log twistd.log.SAVE
twistd -y sample.py
