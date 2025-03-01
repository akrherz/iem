"""Iowa RWIS station plot!"""

from datetime import datetime

from pyiem.database import get_dbconnc
from pyiem.plot import MapPlot


def main():
    """Go Main Go"""
    now = datetime.now()
    pgconn, icursor = get_dbconnc("iem")

    # Compute normal from the climate database
    icursor.execute(
        """
    SELECT
      s.id, tmpf, dwpf, sknt, drct,  ST_x(s.geom) as lon, ST_y(s.geom) as lat
    FROM
      current c, stations s
    WHERE
      s.network IN ('IA_RWIS') and c.iemid = s.iemid and
      valid + '20 minutes'::interval > now() and
      tmpf > -50 and dwpf > -50 and drct is not null
    """
    )
    data = icursor.fetchall()
    pgconn.close()

    mp = MapPlot(
        axisbg="white",
        title="Iowa DOT RWIS Mesoplot",
        subtitle=f"plot valid {now:%-d %b %Y %H:%M %P}",
    )
    mp.plot_station(data)
    mp.drawcounties(color="#EEEEEE")
    pqstr = "plot c 000000000000 iowa_rwis.png bogus png"
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
