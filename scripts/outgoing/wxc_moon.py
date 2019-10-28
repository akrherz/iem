"""
 Generate a WXC formatted file with moon conditions for Iowa sites.  I am
 unsure if the TV folks are still using this or not.  Its easy to generate
"""
from __future__ import print_function
import datetime
import os
import subprocess

import ephem
import pytz
from pyiem.network import Table as NetworkTable

nt = NetworkTable(("AWOS", "IA_ASOS"))


def figurePhase(p1, p2):
    """ Return a string of the moon phase! """
    if p2 > p1:  # Waning!
        if p1 < 0.1:
            return "New Moon"
        if p1 < 0.4:
            return "Waning Crescent"
        if p1 < 0.6:
            return "Last Quarter"
        if p1 < 0.9:
            return "Waning_Gibbous"
        else:
            return "Full Moon"

    else:  # Waxing!
        if p1 < 0.1:
            return "New Moon"
        if p1 < 0.4:
            return "Waxing Crescent"
        if p1 < 0.6:
            return "First Quarter"
        if p1 < 0.9:
            return "Waxing_Gibbous"
        else:
            return "Full Moon"


def mydate(d):
    """ Convert string into a datetime obj """
    if d is None:
        return datetime.datetime(1989, 1, 1)
    if d == "":
        return datetime.datetime(1989, 1, 1)

    gts = datetime.datetime.strptime(str(d), "%Y/%m/%d %H:%M:%S")
    gts = gts.replace(tzinfo=pytz.UTC)
    return gts.astimezone(pytz.timezone("America/Chicago"))


def main():
    """Go Main Go"""
    m = ephem.Moon()

    out = open("/tmp/wxc_moon.txt", "w")
    out.write(
        """Weather Central 001d0300 Surface Data
   8
   4 Station
  30 Location
   6 Lat
   8 Lon
   8 MOON_RISE
   8 MOON_SET
  30 MOON_PHASE
   2 BOGUS
"""
    )

    for station in nt.sts:
        ia = ephem.Observer()
        ia.lat = str(nt.sts[station]["lat"])
        ia.long = str(nt.sts[station]["lon"])
        ia.date = "%s 00:00" % (
            datetime.datetime.utcnow().strftime("%Y/%m/%d"),
        )
        r1 = mydate(ia.next_rising(m))
        s1 = mydate(ia.next_setting(m))
        p1 = m.moon_phase

        ia.date = "%s 00:00" % (
            (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime(
                "%Y/%m/%d"
            ),
        )
        r2 = mydate(ia.next_rising(m))
        s2 = mydate(ia.next_setting(m))
        p2 = m.moon_phase

        mp = figurePhase(p1, p2)
        find_d = datetime.datetime.now().strftime("%Y%m%d")

        my_rise = r2
        if r1.strftime("%Y%m%d") == find_d:
            my_rise = r1

        my_set = s2
        if s1.strftime("%Y%m%d") == find_d:
            my_set = s1

        out.write(
            ("K%s %-30.30s %6.3f %8.3f %8s %8s %30s AA\n")
            % (
                station,
                nt.sts[station]["name"],
                nt.sts[station]["lat"],
                nt.sts[station]["lon"],
                my_rise.strftime("%-I:%M %P"),
                my_set.strftime("%-I:%M %P"),
                mp,
            )
        )

    out.close()

    pqstr = "data c 000000000000 wxc/wxc_moon.txt bogus text"
    cmd = "/home/ldm/bin/pqinsert -p '%s' /tmp/wxc_moon.txt" % (pqstr,)
    subprocess.call(cmd, shell=True)
    os.remove("/tmp/wxc_moon.txt")


if __name__ == "__main__":
    main()
