# Iowa Environmental Mesonet

    If using this code causes your server to have kittens, it is your own fault.

This monolith drives much of the ingest, processing, product generation, and
web presence of the [IEM](https://mesonet.agron.iastate.edu).  Hopefully it can
be found useful for others to at least look at to see how some of the magic happens.

Limited integration testing is done on Travis-CI: [![Build Status](https://travis-ci.com/akrherz/iem.svg)](https://travis-ci.com/akrherz/iem)

## Where are processes running

The processing load for the IEM is spread over a number of virtual machines.
This is an attempt to document what is running where.  The backup shown may not
be automated, but another system that could be up and running the service in
limited time.

Process | Primary | Backup | Monitor
------- | ------- | ------ | -------
Apache ErrorLog | iem12 | None | None
GOES R/S | iem8-dc | iem19 | None
hads-database | metvm4 | None | [check_hads_ingest.py](nagios/check_hads_ingest.py)
iembot  | iem13    | iem12  | nagios checks for twistd processes running
iem-web-services | iem14 | None | None
LDM | iem12 | None | None
LoggerNet | iem12 | None | None
mailman | iem12 | None | None
nwningest | iem12 | None    | cron scripts checks SNET sites for being online
openfire | iem12 | None     | None
postgres | metvm6 | metvm9  | None
samba | iem12 | None | cron scripts check data availability
SSH | iem12 | None | None
RIDGE   | iem13    | None    | inbound file queue, check latency 7 radars
webalizer | iem19 | None | None
Webcam Current | iem13 | None | cron script monitors for offline webcams
Webcam Lapses | iem13 | None | None
