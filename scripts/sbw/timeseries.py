import mx.DateTime
import iemdb
POSTGIS = iemdb.connect('postgis', bypass=True)
pcursor = POSTGIS.cursor()

sts = mx.DateTime.DateTime(2011,4,26,12,0)
ets = mx.DateTime.DateTime(2011,4,28,9,0)
interval = mx.DateTime.RelativeDateTime(minutes=5)
now = sts
maxV = 0
while now < ets:
  sql = """
  SELECT count(*), sum( ST_Area(ST_Transform(geom,2163)) ) from
  sbw_%s where polygon_begin <= %s and polygon_end > %s and
  phenomena = 'TO' 
  """
  #sql = """
  #SELECT count(*), sum( ST_Area(ST_Transform(geom,2163)) ) from
  #warnings_%s where issue <= %s and expire > %s and
  #phenomena = 'TO' and significance = 'A'
  #"""
  pcursor.execute(sql, (now.year, now.strftime("%Y-%m-%d %H:%M"),
		 now.strftime("%Y-%m-%d %H:%M") ))
  row = pcursor.fetchone()
  if row[1] is not None:
    #if row[0] > maxV:
    print '%s,%s,%.3f' % (now.strftime("%Y-%m-%d %H:%M"), row[0],
        row[1] / 1000000.0)
    #  maxV = row[0]
  else:
    print '%s,%s,%.3f' % (now.strftime("%Y-%m-%d %H:%M"),0,0)
  now += interval
