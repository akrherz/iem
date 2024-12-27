"""Plot of current RWIS surface temperatures"""

from zoneinfo import ZoneInfo

import numpy as np
from pyiem.database import get_dbconn
from pyiem.plot import MapPlot
from pyiem.util import utc

IEM = get_dbconn("iem")


def cln(vals):
    """Clean the value for plotting"""
    a = [v for v in vals if v is not None]
    if not a:
        return None
    return np.average(a)


def main():
    """Do Something"""
    cursor = IEM.cursor()
    data = []
    cursor.execute(
        """SELECT ST_x(geom), ST_y(geom), tsf0, tsf1, tsf2, tsf3,
    id, rwis_subf from current c JOIN stations t on (t.iemid = c.iemid)
    WHERE c.valid > now() - '1 hour'::interval and t.network ~* 'RWIS'"""
    )
    for row in cursor:
        val = cln(row[2:6])
        if val is None:
            continue
        d = dict(lat=row[1], lon=row[0], tmpf=val, id=row[6])
        if row[7] is not None and not np.isnan(row[7]):
            d["dwpf"] = row[7]
        data.append(d)

    now = utc().astimezone(ZoneInfo("America/Chicago"))
    mp = MapPlot(
        axisbg="white",
        title="RWIS Average Pavement + Sub-Surface Temperature",
        subtitle=(
            f"Valid: {now:%-d %b %Y %-I:%M %p} "
            "(pavement in red, sub-surface in blue)"
        ),
    )
    mp.plot_station(data)
    mp.drawcounties()
    pqstr = f"plot c {utc():%Y%m%d%H%M} rwis_sf.png rwis_sf.png png"
    mp.postprocess(view=False, pqstr=pqstr)


if __name__ == "__main__":
    main()
