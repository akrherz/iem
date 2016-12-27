"""
 Analysis of current MOS temperature bias
"""
import sys
import psycopg2
from pyiem.plot import MapPlot
import matplotlib.cm as cm
import datetime
import pytz

MOS = psycopg2.connect(database='mos', host='iemdb', user='nobody')
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
mcursor = MOS.cursor()
icursor = IEM.cursor()


def doit(now, model):
    """ Figure out the model runtime we care about """
    mcursor.execute("""
    SELECT max(runtime at time zone 'UTC') from alldata where station = 'KDSM'
    and ftime = %s and model = %s
    """, (now, model))
    row = mcursor.fetchone()
    runtime = row[0]
    if runtime is None:
        sys.exit()
    runtime = runtime.replace(tzinfo=pytz.timezone("UTC"))

    # Load up the mos forecast for our given
    mcursor.execute("""
      SELECT station, tmp FROM alldata
    WHERE model = %s and runtime = %s and ftime = %s and tmp < 999
    """, (model, runtime, now))
    forecast = {}
    for row in mcursor:
        if row[0][0] == 'K':
            forecast[row[0][1:]] = row[1]

    # Load up the currents!
    icursor.execute("""
    SELECT
      s.id, s.network, tmpf, ST_x(s.geom) as lon, ST_y(s.geom) as lat
    FROM
      current c, stations s
    WHERE
      c.iemid = s.iemid and
      (s.network ~* 'ASOS' or s.network = 'AWOS') and s.country = 'US' and
      valid + '60 minutes'::interval > now() and
      tmpf > -50
    """)

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

    cmap = cm.get_cmap("RdYlBu_r")
    cmap.set_under('black')
    cmap.set_over('black')

    localnow = now.astimezone(pytz.timezone("America/Chicago"))
    m = MapPlot(sector='midwest',
                title="%s MOS Temperature Bias " % (model,),
                subtitle=('Model Run: %s Forecast Time: %s'
                          ) % (runtime.strftime("%d %b %Y %H %Z"),
                               localnow.strftime("%d %b %Y %-I %p %Z")))
    m.contourf(lons, lats, vals, range(-10, 11, 2), units='F', cmap=cmap)

    pqstr = "plot ac %s00 %s_mos_T_bias.png %s_mos_T_bias_%s.png png" % (
                now.strftime("%Y%m%d%H"), model.lower(),
                model.lower(), now.strftime("%H"))
    m.postprocess(pqstr=pqstr, view=False)
    m.close()

    m = MapPlot(sector='conus',
                title="%s MOS Temperature Bias " % (model,),
                subtitle=('Model Run: %s Forecast Time: %s'
                          ) % (runtime.strftime("%d %b %Y %H %Z"),
                               localnow.strftime("%d %b %Y %-I %p %Z")))
    m.contourf(lons, lats, vals, range(-10, 11, 2), units='F', cmap=cmap)

    pqstr = ("plot ac %s00 conus_%s_mos_T_bias.png "
             "conus_%s_mos_T_bias_%s.png png"
             ) % (now.strftime("%Y%m%d%H"), model.lower(),
                  model.lower(), now.strftime("%H"))
    m.postprocess(pqstr=pqstr, view=False)


def main():
    """ Go main go"""
    ts = datetime.datetime.utcnow()
    model = sys.argv[1]
    if len(sys.argv) == 6:
        ts = datetime.datetime(int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]), int(sys.argv[4]))
        model = sys.argv[5]
    ts = ts.replace(minute=0, second=0, microsecond=0)
    ts = ts.replace(tzinfo=pytz.timezone("UTC"))
    doit(ts, model)

if __name__ == "__main__":
    main()
