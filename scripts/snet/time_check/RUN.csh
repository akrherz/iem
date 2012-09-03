#!/bin/sh

kill -9 `cat twistd.pid`
sleep 1
mv twistd.log twistd.log.SAVE
twistd -y sample.py
