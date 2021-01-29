"""
 Generate a WXC formatted file with moon conditions for Iowa sites. At least
 one TV station is using this.

 Run from RUN_MIDNIGHT.sh
"""
# stdlib
import datetime
import os
import subprocess

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

# third party
import ephem
from pyiem.util import utc, logger
from pyiem.network import Table as NetworkTable

LOG = logger()
nt = NetworkTable(("AWOS", "IA_ASOS"))
UTC = datetime.timezone.utc


def figurePhase(p1, p2):
    """ Return a string of the moon phase! """
    if p2 < p1:  # Waning!
        if p1 < 0.1:
            return "New Moon"
        if p1 < 0.4:
            return "Waning Crescent"
        if p1 < 0.6:
            return "Last Quarter"
        if p1 < 0.9:
            return "Waning Gibbous"
        return "Full Moon"

    if p1 < 0.1:
        return "New Moon"
    if p1 < 0.4:
        return "Waxing Crescent"
    if p1 < 0.6:
        return "First Quarter"
    if p1 < 0.9:
        return "Waxing Gibbous"
    return "Full Moon"


def main():
    """Go Main Go"""
    m = ephem.Moon()

    out = open("/tmp/wxc_moon.txt", "w")
    out.write(
        """Weather Central 001d0300 Surface Data
   9
   4 Station
  30 Location
   6 Lat
   8 Lon
  19 MOON_RISE
  19 MOON_SET
  30 MOON_PHASE
   6 PERCENT ILLUMINATED
   2 BOGUS
"""
    )

    # Compute midnight tomorrow
    tm = utc() + datetime.timedelta(days=1)
    tz = ZoneInfo("America/Chicago")
    midnight = datetime.datetime(tm.year, tm.month, tm.day, tzinfo=tz)
    utc_midnight = midnight.astimezone(UTC)
    LOG.debug("midnight is %s", midnight)
    for station in nt.sts:
        ia = ephem.Observer()
        ia.lat = str(nt.sts[station]["lat"])
        ia.long = str(nt.sts[station]["lon"])
        # Figure out the first rise after midnight
        ia.date = utc_midnight.strftime("%Y/%m/%d %H:00")
        r1 = ia.next_rising(m).datetime().replace(tzinfo=UTC)
        # Figure out when it sets after this date
        ia.date = r1.strftime("%Y/%m/%d %H:%M")
        s1 = ia.next_setting(m).datetime().replace(tzinfo=UTC)
        LOG.debug("r1: %s s1: %s", r1, s1)
        p1 = m.moon_phase

        # Get the next rise after the first set
        ia.date = s1.strftime("%Y/%m/%d %H:%M")
        # to advance API?
        ia.next_rising(m)
        p2 = m.moon_phase
        LOG.debug("p1: %s p2: %s", p1, p2)

        mp = figurePhase(p1, p2)

        out.write(
            ("K%s %-30.30s %6.3f %8.3f %19s %19s %30s %6.2f AA\n")
            % (
                station,
                nt.sts[station]["name"],
                nt.sts[station]["lat"],
                nt.sts[station]["lon"],
                r1.astimezone(tz).strftime("%Y/%m/%d %-I:%M %P"),
                s1.astimezone(tz).strftime("%Y/%m/%d %-I:%M %P"),
                mp,
                p1 * 100.0,
            )
        )

    out.close()

    pqstr = "data c 000000000000 wxc/wxc_moon.txt bogus text"
    cmd = "pqinsert -p '%s' /tmp/wxc_moon.txt" % (pqstr,)
    subprocess.call(cmd, shell=True)
    os.remove("/tmp/wxc_moon.txt")


if __name__ == "__main__":
    main()
