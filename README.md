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
GOES R/S | iem8-dc | iem19 | None
iembot  | iem13    | iem12  | nagios checks for twistd processes running
iem-web-services | iem16 | iem14 | None
LDM | iem14 | None | None
LoggerNet | iem15 | None | None
NEXRAD Mosaics | iem8-dc | iem16 | nagios checks archive
openfire | iem16 | iem14 | None
postgres | metvm2 | metvm9  | None
postgres4 | metvm7 | None | None
samba | iem12 | None | cron scripts check data availability
SSH | iem14 | None | None
RIDGE   | iem13    | None    | inbound file queue, check latency 7 radars
webalizer | iem19 | None | None
Webcam Current | iem13 | None | cron script monitors for offline webcams
Webcam Lapses | iem13 | None | None
