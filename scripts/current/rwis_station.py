"""Iowa RWIS station plot!
"""
import datetime
import psycopg2.extras
from pyiem.plot import MapPlot
from pyiem.util import get_dbconn


def main():
    """Go Main Go"""
    now = datetime.datetime.now()
    pgconn = get_dbconn("iem", user="nobody")
    icursor = pgconn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Compute normal from the climate database
    sql = """
    SELECT
      s.id, tmpf, dwpf, sknt, drct,  ST_x(s.geom) as lon, ST_y(s.geom) as lat
    FROM
      current c, stations s
    WHERE
      s.network IN ('IA_RWIS') and c.iemid = s.iemid and
      valid + '20 minutes'::interval > now() and
      tmpf > -50 and dwpf > -50
    """

    data = []
    icursor.execute(sql)
    for row in icursor:
        data.append(row)

    mp = MapPlot(
        axisbg="white",
        title="Iowa DOT RWIS Mesoplot",
        subtitle="plot valid %s" % (now.strftime("%-d %b %Y %H:%M %P"),),
    )
    mp.plot_station(data)
    mp.drawcounties(color="#EEEEEE")
    pqstr = "plot c 000000000000 iowa_rwis.png bogus png"
    mp.postprocess(pqstr=pqstr)
    mp.close()


if __name__ == "__main__":
    main()
