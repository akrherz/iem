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
Apache ErrorLog | iem12 | None | None
GOES R/S | iem8-dc | iem19 | None
hads-database | metvm4 | None | [check_hads_ingest.py](https://github.com/akrherz/nagios-checks)
iembot  | iem13    | iem12  | nagios checks for twistd processes running
iem-web-services | iem14 | iem16 | None
LDM | iem12 | None | None
LoggerNet | iem12 | None | None
mailman | iem12 | None | None
nwningest | iem12 | None    | cron scripts checks SNET sites for being online
openfire | iem12 | None     | None
postgres | metvm6 | metvm9  | None
postgres2 | metvm4 | None | None
postgres3 | metvm1 | None | None
postgres4 | metvm7 | None | None
samba | iem12 | None | cron scripts check data availability
SSH | iem12 | None | None
RIDGE   | iem13    | None    | inbound file queue, check latency 7 radars
webalizer | iem19 | None | None
Webcam Current | iem13 | None | cron script monitors for offline webcams
Webcam Lapses | iem13 | None | None
