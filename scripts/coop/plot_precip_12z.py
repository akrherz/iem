"""
Generate simple plots of 12z COOP preciptiation

Called from RUN_COOP.sh
"""

import warnings
from datetime import date, datetime

import click
from psycopg import Connection
from pyiem.database import get_sqlalchemy_conn
from pyiem.network import Table as NetworkTable
from pyiem.plot import MapPlot
from sqlalchemy import text

warnings.simplefilter("ignore", UserWarning)


def doit(conn: Connection, dt: date) -> None:
    """
    Generate some plots for the COOP data!
    """
    st = NetworkTable(
        (
            "IA_COOP MO_COOP KS_COOP NE_COOP SD_COOP ND_ASOS"
            "MN_COOP WI_COOP IL_COOP IN_COOP OH_COOP MI_COOP"
        ).split()
    )

    clevs = [0, 0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1, 2, 3, 4, 5, 10]
    # We'll assume all COOP data is 12z, sigh for now
    res = conn.execute(
        text(f"""SELECT id, pday, network
           from summary_{dt:%Y} s JOIN stations t ON (t.iemid = s.iemid)
           WHERE day = :dt and
           t.network ~* 'COOP' and pday >= 0"""),
        {"dt": dt},
    )

    lats = []
    lons = []
    vals = []
    iamax = 0.0
    for row in res:
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
        subtitle=f"Ending {dt:%d %B %Y} at roughly 12 UTC",
    )

    mp.contourf(lons, lats, vals, clevs, units="inch")

    pqstr = (
        f"plot ac {dt:%Y%m%d}0000 iowa_coop_12z_precip.png "
        "iowa_coop_12z_precip.png png"
    )
    mp.drawcounties()
    mp.postprocess(pqstr=pqstr)
    mp.close()

    mp = MapPlot(
        sector="midwest",
        title="24 Hour NWS COOP Precipitation [inch]",
        subtitle=f"Ending {dt:%d %B %Y} at roughly 12 UTC",
    )

    mp.contourf(lons, lats, vals, clevs, units="inch")

    pqstr = (
        f"plot ac {dt:%Y%m%d}0000 midwest_coop_12z_precip.png "
        "midwest_coop_12z_precip.png png"
    )
    mp.postprocess(pqstr=pqstr)
    mp.close()


@click.command()
@click.option(
    "--date",
    "dt",
    required=True,
    type=click.DateTime(),
    help="Date to process",
)
def main(dt: datetime):
    """Go Main Go"""
    with get_sqlalchemy_conn("iem") as conn:
        doit(conn, dt.date())


if __name__ == "__main__":
    main()
