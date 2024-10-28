"""Analysis of current MOS temperature bias."""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import click
from pyiem.database import get_dbconn
from pyiem.plot import MapPlot, get_cmap
from pyiem.util import logger, utc

LOG = logger()


def doit(now, model):
    """Figure out the model runtime we care about"""
    mos_pgconn = get_dbconn("mos")
    iem_pgconn = get_dbconn("iem")
    mcursor = mos_pgconn.cursor()
    icursor = iem_pgconn.cursor()
    mcursor.execute(
        "SELECT max(runtime at time zone 'UTC') from alldata "
        "where station = 'KDSM' and ftime = %s and model = %s",
        (now, model),
    )
    row = mcursor.fetchone()
    runtime = row[0]
    if runtime is None:
        LOG.info("Model %s runtime %s not found, abort", model, now)
        return
    runtime = runtime.replace(tzinfo=ZoneInfo("UTC"))

    # Load up the mos forecast for our given
    mcursor.execute(
        "SELECT station, tmp FROM alldata "
        "WHERE model = %s and runtime = %s and ftime = %s and tmp < 999",
        (model, runtime, now),
    )
    forecast = {}
    for row in mcursor:
        if row[0][0] == "K":
            forecast[row[0][1:]] = row[1]

    # Load up the currents!
    icursor.execute(
        """
        SELECT
        s.id, s.network, tmpf, ST_x(s.geom) as lon, ST_y(s.geom) as lat
        FROM
        current c, stations s
        WHERE
        c.iemid = s.iemid and
        s.network ~* 'ASOS' and s.country = 'US' and
        valid + '60 minutes'::interval > now() and
        tmpf > -50
    """
    )

    lats = []
    lons = []
    vals = []
    for row in icursor:
        if row[0] not in forecast:
            continue

        diff = forecast[row[0]] - row[2]
        if diff > 20 or diff < -20:
            continue
        lats.append(row[4])
        lons.append(row[3])
        vals.append(diff)

    cmap = get_cmap("RdYlBu_r")
    cmap.set_under("black")
    cmap.set_over("black")

    localnow = now.astimezone(ZoneInfo("America/Chicago"))
    subtitle = (
        f"Model Run: {runtime:%d %b %Y %H %Z} "
        f"Forecast Time: {localnow:%d %b %Y %-I %p %Z}"
    )
    mp = MapPlot(
        sector="conus",
        title=f"{model} MOS Temperature Bias",
        subtitle=subtitle,
    )
    mp.contourf(lons, lats, vals, range(-10, 11, 2), units="F", cmap=cmap)

    pqstr = (
        f"plot ac {now:%Y%m%d%H}00 conus_{model.lower()}_mos_T_bias.png "
        f"conus_{model.lower()}_mos_T_bias_{now:%H}.png png"
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()


@click.command()
@click.option("--model", required=True)
@click.option("--valid", type=click.DateTime())
def main(model: str, valid: Optional[datetime]):
    """Go main go"""
    ts = utc()
    if valid is not None:
        ts = valid.replace(tzinfo=ZoneInfo("UTC"))
    ts = ts.replace(minute=0, second=0, microsecond=0)
    doit(ts, model)


if __name__ == "__main__":
    main()
