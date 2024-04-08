"""
Generate simple plots of 12z COOP preciptiation
"""

import datetime
import sys
import warnings

from pyiem.database import get_dbconn
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot

warnings.simplefilter("ignore", UserWarning)


def doit(now):
    """
    Generate some plots for the COOP data!
    """
    st = NetworkTable(
        (
            "IA_COOP MO_COOP KS_COOP NE_COOP SD_COOP ND_ASOS"
            "MN_COOP WI_COOP IL_COOP IN_COOP OH_COOP MI_COOP"
        ).split()
    )

    pgconn = get_dbconn("iem")
    icursor = pgconn.cursor()

    clevs = [0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 2, 3, 4, 5, 10]
    # We'll assume all COOP data is 12z, sigh for now
    sql = """SELECT id, pday, network
           from summary_%s s JOIN stations t ON (t.iemid = s.iemid)
           WHERE day = '%s' and
           t.network ~* 'COOP' and pday >= 0""" % (
        now.year,
        now.strftime("%Y-%m-%d"),
    )

    lats = []
    lons = []
    vals = []
    icursor.execute(sql)
    iamax = 0.0
    for row in icursor:
        sid = row[0]
        if sid not in st.sts:
            continue
        lats.append(st.sts[sid]["lat"])
        lons.append(st.sts[sid]["lon"])
        vals.append(row[1])
        if row[2] == "IA_COOP" and row[1] > iamax:
            iamax = row[1]

    # Plot Iowa
    mp = MapPlot(
        sector="iowa",
        title="24 Hour NWS COOP Precipitation [inch]",
        subtitle=("Ending %s at roughly 12Z") % (now.strftime("%d %B %Y"),),
    )

    mp.contourf(lons, lats, vals, clevs, units="inch")

    pqstr = (
        "plot ac %s0000 iowa_coop_12z_precip.png "
        "iowa_coop_12z_precip.png png"
    ) % (now.strftime("%Y%m%d"),)
    mp.drawcounties()
    mp.postprocess(pqstr=pqstr)
    mp.close()

    mp = MapPlot(
        sector="midwest",
        title="24 Hour NWS COOP Precipitation [inch]",
        subtitle=("Ending %s at roughly 12Z") % (now.strftime("%d %B %Y"),),
    )

    mp.contourf(lons, lats, vals, clevs, units="inch")

    pqstr = (
        "plot ac %s0000 midwest_coop_12z_precip.png "
        "midwest_coop_12z_precip.png png"
    ) % (now.strftime("%Y%m%d"),)
    mp.postprocess(pqstr=pqstr)
    mp.close()


def main():
    """Go Main Go"""
    ts = datetime.datetime.now()
    if len(sys.argv) == 4:
        ts = datetime.datetime(
            int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
        )
    doit(ts)


if __name__ == "__main__":
    main()
