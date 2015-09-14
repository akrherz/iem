It this causes your server to have kittens, it is your own fault.

Some IEM cluster details (so I can keep it straight!)

-[ ] one
-[x] two

# Point php.ini at memcache for sessions
[Session]
session.save_handler = memcache
session.save_path = "tcp://iem-memcached:11211"

# Considerations prior to rebooting a machine

* make sure LDM cleanly stops
* check nagios after reboot :)

Machine | Needs
--------+-------
iem21   | webcam lapses
iem30   | None
iem50   | migrate 202 VIP over to iem30 

# Where are processes running?!?

Process | Primary | Backup | Monitor?
--------+---------+--------+---------
RIDGE   | iem6    | ???    | inbound file queue, check latency 7 radars
Webcam Lapses | iem6 | ??? | None
Webcam Current | iem6 | ??? | cron script monitors for offline webcams
iembot  | iem6    | iem21  | nagios checks for twistd processes running
nwningest | iem12 | ???    | cron scripts checks SNET sites for being online
openfire | iem12 | ???     | None
postgres | metvm4 | iemfe  | None

#Shared Filesystems

    /mnt/gluster0 :: iem-dr{1,2} clustered replica meant for larger files
    /mnt/mesonet  :: primary /mesonet folder from iem21
    /mnt/mesonet2 :: secondary /mesonet folder from iemvm1
