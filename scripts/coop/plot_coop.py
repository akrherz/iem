"""Plot of Precip reports"""
import datetime

from pyiem.reference import TRACE_VALUE
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def pretty(val, precision=2):
    """Make a value into a prettier string

    Args:
      val (float): value to convert to a string
      precision (int): number of places
    """
    if val == 0:
        return "0"
    if val == TRACE_VALUE:
        return "T"
    return ("%." + str(precision) + "f") % (val,)


def plot_hilo(valid):
    """Go Main Go

    Args:
      valid (datetime): The timestamp we are interested in!
    """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT max_tmpf, min_tmpf, id, st_x(geom), st_y(geom)
    from summary s JOIN stations t on
    (t.iemid = s.iemid) WHERE s.day = %s
    and t.network in ('IA_COOP', 'NE_COOP', 'MO_COOP', 'IL_COOP', 'WI_COOP',
    'MN_COOP')
    and max_tmpf is not null and max_tmpf >= -30 and
    min_tmpf is not null and min_tmpf < 99 and
    extract(hour from coop_valid) between 5 and 10""",
        (valid.date(),),
    )
    data = []
    for row in cursor:
        data.append(
            dict(lat=row[4], lon=row[3], tmpf=row[0], dwpf=row[1], id=row[2])
        )

    mp = MapPlot(
        title=(r"%s NWS COOP 24 Hour High/Low Temperature [$^\circ$F]")
        % (valid.strftime("%-d %b %Y"),),
        subtitle="Reports valid between 6 and 9 AM",
        axisbg="white",
        figsize=(10.24, 7.68),
    )
    mp.plot_station(data)
    mp.drawcounties()

    pqstr = "plot ac %s0000 coopHighLow.gif coopHighLow.gif gif" % (
        valid.strftime("%Y%m%d"),
    )

    mp.postprocess(pqstr=pqstr)
    mp.close()

    pgconn.close()


def plot_snowdepth(valid):
    """Go Main Go

    Args:
      valid (datetime): The timestamp we are interested in!
    """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT snowd, id, st_x(geom), st_y(geom)
    from summary s JOIN stations t on
    (t.iemid = s.iemid) WHERE s.day = %s
    and t.network in ('IA_COOP', 'NE_COOP', 'MO_COOP', 'IL_COOP', 'WI_COOP',
    'MN_COOP')
    and snowd is not null and snowd >= 0 and
    extract(hour from coop_valid) between 5 and 10""",
        (valid.date(),),
    )
    labels = []
    vals = []
    lats = []
    lons = []
    for row in cursor:
        labels.append(row[1])
        vals.append(pretty(row[0], precision=0))
        lats.append(row[3])
        lons.append(row[2])

    mp = MapPlot(
        title="%s NWS COOP Snowfall Depth Reports [inch]"
        % (valid.strftime("%-d %b %Y"),),
        subtitle="Reports valid between 6 and 9 AM",
        axisbg="white",
        figsize=(10.24, 7.68),
    )
    mp.plot_values(lons, lats, vals, fmt="%s", labels=labels, labelcolor="tan")
    mp.drawcounties()

    pqstr = "plot ac %s0000 coopSnowDepth.gif coopSnowDepth.gif gif" % (
        valid.strftime("%Y%m%d"),
    )

    mp.postprocess(pqstr=pqstr)
    mp.close()

    pgconn.close()


def plot_snow(valid):
    """Go Main Go

    Args:
      valid (datetime): The timestamp we are interested in!
    """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT snow, id, st_x(geom), st_y(geom)
    from summary s JOIN stations t on
    (t.iemid = s.iemid) WHERE s.day = %s
    and t.network in ('IA_COOP', 'NE_COOP', 'MO_COOP', 'IL_COOP', 'WI_COOP',
    'MN_COOP')
    and snow is not null and snow >= 0 and
    extract(hour from coop_valid) between 5 and 10""",
        (valid.date(),),
    )
    labels = []
    vals = []
    lats = []
    lons = []
    for row in cursor:
        labels.append(row[1])
        vals.append(pretty(row[0]))
        lats.append(row[3])
        lons.append(row[2])

    mp = MapPlot(
        title="%s NWS COOP 24 Hour Snowfall Reports [inch]"
        % (valid.strftime("%-d %b %Y"),),
        subtitle="Reports valid between 6 and 9 AM",
        axisbg="white",
        figsize=(10.24, 7.68),
    )
    mp.plot_values(lons, lats, vals, fmt="%s", labels=labels, labelcolor="tan")
    mp.drawcounties()

    pqstr = "plot ac %s0000 coopSnowPlot.gif coopSnowPlot.gif gif" % (
        valid.strftime("%Y%m%d"),
    )

    mp.postprocess(pqstr=pqstr)
    mp.close()

    pgconn.close()


def plot_snow_month(valid):
    """Go Main Go

    Args:
      valid (datetime): The timestamp we are interested in!
    """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    d1 = valid.replace(day=1)
    d2 = d1 + datetime.timedelta(days=35)
    d2 = d2.replace(day=1)

    cursor.execute(
        """SELECT sum(snow), id, st_x(geom), st_y(geom)
    from summary s JOIN stations t on
    (t.iemid = s.iemid) WHERE s.day >= %s and s.day < %s
    and t.network in ('IA_COOP', 'NE_COOP', 'MO_COOP', 'IL_COOP', 'WI_COOP',
    'MN_COOP')
    and snow is not null and snow >= 0 and
    extract(hour from coop_valid) between 5 and 10
    GROUP by id, st_x, st_y""",
        (d1.date(), d2.date()),
    )
    labels = []
    vals = []
    lats = []
    lons = []
    for row in cursor:
        labels.append(row[1])
        vals.append(pretty(row[0], 0))
        lats.append(row[3])
        lons.append(row[2])

    mp = MapPlot(
        title="%s NWS COOP Month Snowfall Totals [inch]"
        % (valid.strftime("%-d %b %Y"),),
        subtitle="Reports valid between 6 and 9 AM",
        axisbg="white",
        figsize=(10.24, 7.68),
    )
    mp.plot_values(lons, lats, vals, fmt="%s", labels=labels, labelcolor="tan")
    mp.drawcounties()

    pqstr = "plot ac %s0000 coopMonthSPlot.gif coopMonthSPlot.gif gif" % (
        valid.strftime("%Y%m%d"),
    )

    mp.postprocess(pqstr=pqstr)
    mp.close()

    pgconn.close()


def plot_precip_month(valid):
    """Go Main Go

    Args:
      valid (datetime): The timestamp we are interested in!
    """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    d1 = valid.replace(day=1)
    d2 = d1 + datetime.timedelta(days=35)
    d2 = d2.replace(day=1)

    cursor.execute(
        """SELECT sum(pday), id, st_x(geom), st_y(geom)
    from summary s JOIN stations t on
    (t.iemid = s.iemid) WHERE s.day >= %s and s.day < %s
    and t.network in ('IA_COOP', 'NE_COOP', 'MO_COOP', 'IL_COOP', 'WI_COOP',
    'MN_COOP')
    and pday is not null and pday >= 0 and
    extract(hour from coop_valid) between 5 and 10
    GROUP by id, st_x, st_y""",
        (d1.date(), d2.date()),
    )
    labels = []
    vals = []
    lats = []
    lons = []
    for row in cursor:
        labels.append(row[1])
        vals.append(pretty(row[0]))
        lats.append(row[3])
        lons.append(row[2])

    mp = MapPlot(
        title="%s NWS COOP Month Precipitation Totals [inch]"
        % (valid.strftime("%-d %b %Y"),),
        subtitle="Reports valid between 6 and 9 AM",
        axisbg="white",
        figsize=(10.24, 7.68),
    )
    mp.plot_values(lons, lats, vals, fmt="%s", labels=labels, labelcolor="tan")
    mp.drawcounties()

    pqstr = "plot ac %s0000 coopMonthPlot.gif coopMonthPlot.gif gif" % (
        valid.strftime("%Y%m%d"),
    )

    mp.postprocess(pqstr=pqstr)
    mp.close()

    pgconn.close()


def plot_precip(valid):
    """Go Main Go

    Args:
      valid (datetime): The timestamp we are interested in!
    """
    pgconn = get_dbconn("iem")
    cursor = pgconn.cursor()

    cursor.execute(
        """SELECT pday, id, st_x(geom), st_y(geom)
    from summary s JOIN stations t on
    (t.iemid = s.iemid) WHERE s.day = %s
    and t.network in ('IA_COOP', 'NE_COOP', 'MO_COOP', 'IL_COOP', 'WI_COOP',
    'MN_COOP')
    and pday is not null and pday >= 0 and
    extract(hour from coop_valid) between 5 and 10""",
        (valid.date(),),
    )
    labels = []
    vals = []
    lats = []
    lons = []
    for row in cursor:
        labels.append(row[1])
        vals.append(pretty(row[0]))
        lats.append(row[3])
        lons.append(row[2])

    mp = MapPlot(
        title="%s NWS COOP 24 Hour Precipitation Reports [inch]"
        % (valid.strftime("%-d %b %Y"),),
        subtitle="Reports valid between 6 and 9 AM",
        axisbg="white",
        figsize=(10.24, 7.68),
    )
    mp.plot_values(lons, lats, vals, fmt="%s", labels=labels, labelcolor="tan")
    mp.drawcounties()

    pqstr = "plot ac %s0000 coopPrecPlot.gif coopPrecPlot.gif gif" % (
        valid.strftime("%Y%m%d"),
    )

    mp.postprocess(pqstr=pqstr)
    mp.close()

    pgconn.close()


if __name__ == "__main__":
    plot_precip(datetime.datetime.now())
    plot_snow(datetime.datetime.now())
    plot_snowdepth(datetime.datetime.now())
    plot_hilo(datetime.datetime.now())
    plot_precip_month(datetime.datetime.now())
    plot_snow_month(datetime.datetime.now())
