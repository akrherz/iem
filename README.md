# Iowa Environmental Mesonet

    If using this code causes your server to have kittens, it is your own fault.

This monolith drives much of the ingest, processing, product generation, and
web presence of the [IEM](https://mesonet.agron.iastate.edu).  Hopefully it can
be found useful for others to at least look at to see how some of the magic happens.

Limited integration testing is done on Github Actions: [![Build Status](https://github.com/akrherz/iem/workflows/Install%20and%20Test/badge.svg)](https://github.com/akrherz/iem)

Database schema is in [akrherz/iem-database](https://github.com/akrherz/iem-database).

## Where are processes running

The processing load for the IEM is spread over a number of virtual machines.
This is an attempt to document what is running where.  The backup shown may not
be automated, but another system that could be up and running the service in
limited time.

Process | Primary | Backup | Monitor
------- | ------- | ------ | -------
AWOS Ingest | iem19 | iem14 | nagios `check_awos_ingest.py`
GOES R/S | iem8-dc | iem19 | None
hrrr | iem8-dc | None | None
iembot  | iem19    | None  | nagios checks for twistd processes running
iemdb1 | metvm4 | metvm8 | nagios check
iemdb2 | metvm2 | metvm0 | nagios check
iemdb3 | metvm6 | metvm1 | nagios check
iem-web-services | iem12 | iem19 | nagios check
letsencrpyt | iem19 | None | nagios SSL check
LDM | iem14 | None | None
LoggerNet | iem8-dc | None | nagios check
memcached | iem8-dc | iem11-dc | nagios check
NEXRAD Mosaics | iem8-dc | iem16 | nagios checks archive
NWWS-OI Ingest | iem12 | None | None
openfire | iem19 | None | None
rabbitmq | iem9-dc | iem8-dc | nagios check
samba | iem16 | None | cron scripts check data availability
RIDGE | iem9-dc | None    | inbound file queue, check latency 7 radars
webalizer | iem19 | None | None
Webcam Current | iem18 | None | cron script monitors for offline webcams
Webcam Lapses | iem18 | None | None
