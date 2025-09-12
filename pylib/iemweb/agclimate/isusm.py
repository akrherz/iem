"""
Generate various plots for ISUSM data
"""

from io import BytesIO

from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from pyiem.util import c2f
from pyiem.webutil import iemapp

CTX = {
    "tmpf": {"title": "2m Air Temperature [F]"},
    "rh": {"title": "2m Air Humidity [%]"},
    "high": {"title": "Today's High Temp [F]"},
}


def get_currents():
    """Return dict of current values"""
    dbconn = get_dbconn("iem")
    cursor = dbconn.cursor()
    dbconn2 = get_dbconn("isuag")
    cursor2 = dbconn2.cursor()
    data = {}
    cursor.execute(
        """
    SELECT id, valid, tmpf, relh from current c JOIN stations t on
    (t.iemid = c.iemid) WHERE valid > now() - '3 hours'::interval and
    t.network = 'ISUSM'
    """
    )
    valid = None
    for row in cursor:
        data[row[0]] = {
            "tmpf": row[2],
            "rh": row[3],
            "valid": row[1],
            "high": None,
        }
        if valid is None:
            valid = row[1]

    # Go get daily values
    cursor2.execute(
        "SELECT station, tair_c_max_qc from sm_daily where valid = %s",
        (valid,),
    )
    for row in cursor2:
        data[row[0]]["high"] = c2f(row[1])

    cursor.close()
    dbconn.close()
    return data


def plot(data, v):
    """Actually plot this data"""
    nt = NetworkTable("ISUSM")
    lats = []
    lons = []
    vals = []
    valid = None
    for sid in data.keys():
        if data[sid][v] is None:
            continue
        lats.append(nt.sts[sid]["lat"])
        lons.append(nt.sts[sid]["lon"])
        vals.append(data[sid][v])
        valid = data[sid]["valid"]

    if valid is None:
        mp = MapPlot(
            sector="iowa",
            axisbg="white",
            title=f"ISU Soil Moisture Network :: {CTX[v]['title']}",
            figsize=(8.0, 6.4),
        )
        mp.plot_values([-95], [41.99], ["No Data Found"], "%s", textsize=30)
        return mp

    mp = MapPlot(
        sector="iowa",
        axisbg="white",
        title=f"ISU Soil Moisture Network :: {CTX[v]['title']}",
        subtitle=f"valid {valid:%-d %B %Y %I:%M %p}",
        figsize=(8.0, 6.4),
    )
    mp.plot_values(lons, lats, vals, "%.1f")
    mp.drawcounties()
    return mp


@iemapp()
def application(environ, start_response):
    """Go Main Go"""
    v = environ.get("v", "tmpf")
    data = get_currents()
    mp = plot(data, v)
    bio = BytesIO()
    mp.fig.savefig(bio)

    headers = [("Content-type", "image/png")]
    start_response("200 OK", headers)
    return [bio.getvalue()]
