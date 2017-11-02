import sys

from pyiem.util import get_dbconn
pgconn = get_dbconn('postgis')
cursor = pgconn.cursor()
cursor2 = pgconn.cursor()

data = {}
total = {'cnt': 0, 'hundreds': 0, 'zeroes': 0, 'sum_shared': 0,
         'sum_perimeter': 0, 'sum_area': 0}


# Select all SV,TO SBWs
cursor.execute("""
    SELECT issue, phenomena, eventid, wfo,
    ST_perimeter(ST_transform(geom,2163)) as perimeter,
    ST_area(ST_transform(geom,2163)) / 1000000.0 as area
    from sbw
    WHERE gtype = 'P' and phenomena IN ('SV', 'TO')
    and issue > '2007-10-01'
    """)

for row in cursor:
    wfo = row[3]
    eventid = row[2]
    phenomena = row[1]
    perimeter = row[4]
    area = row[5]
    if perimeter == 0:
        continue

    sql = """
SELECT sum(sz) as s from (
     SELECT length(transform(a,2163)) as sz from (
        select
           intersection(
      buffer(exteriorring(geometryn(multi(geomunion(n.geom)),1)),0.02),
      exteriorring(geometryn(multi(geomunion(w.geom)),1))
            )  as a
            from warnings_%s w, nws_ugc n WHERE gtype = 'P'
            and w.wfo = '%s' and phenomena = '%s' and eventid = '%s'
            and significance = 'W' and n.polygon_class = 'C'
            and st_overlaps(n.geom, w.geom) 
            and n.ugc IN (
                SELECT ugc from warnings_%s WHERE
                gtype = 'C' and wfo = '%s' 
          and phenomena = '%s' and eventid = '%s' and significance = 'W'
       )
         ) as foo
            WHERE not isempty(a) ) as foo""" % (year, wfo, phenomena, eventid,
          year, wfo, phenomena, eventid)
    try:
        rs2 = postgis.query(sql).dictresult()
    except:
        continue
    if len(rs2) == 0:
        continue

    shared = rs2[0]['s']
    if shared is None:
        shared = 0
    if not data.has_key(wfo):
        data[wfo] = {'cnt': 0, 'hundreds': 0, 'zeroes': 0, 'sum_shared': 0, 
                     'sum_perimeter': 0}
    ratio = shared / perimeter * 100
    if ratio > 97:
        data[wfo]['hundreds'] += 1
    if ratio < 3:
        data[wfo]['zeroes'] += 1
    data[wfo]['sum_shared'] += shared
    data[wfo]['sum_perimeter'] += perimeter
    data[wfo]['cnt'] += 1
    total['cnt'] += 1
    total['sum_perimeter'] += perimeter
    total['sum_shared'] += shared
    total['sum_area'] += area
    if ratio > 97:
        total['hundreds'] += 1
    if ratio < 3:
        total['zeroes'] += 1


#for wfo in data.keys():
#    print '%s,%s,%s,%s,%.2f' % (wfo, data[wfo]['cnt'],
#          data[wfo]['zeroes'], data[wfo]['hundreds'],
#          data[wfo]['sum_shared'] / data[wfo]['sum_perimeter'] * 100)

print '%s,%s,%s,%s,%.2f,%.2f' % (year, total['cnt'],
          total['zeroes'], total['hundreds'],
          total['sum_shared'] / total['sum_perimeter'] * 100,
           total['sum_area'] / float(total['cnt']) )

