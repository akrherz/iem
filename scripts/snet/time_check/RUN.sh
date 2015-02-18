#!/bin/sh

if [ -e twistd.pid ]; then
	kill -9 `cat twistd.pid`
	sleep 1
fi
if [ -e twistd.log ]; then
	rm twistd.log
fi
twistd -y sample.py
