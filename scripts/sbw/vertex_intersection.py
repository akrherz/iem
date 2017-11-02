
from pyiem.util import get_dbconn
from pyiem.network import Table as NetworkTable

pgconn = get_dbconn('postgis')
cursor = pgconn.cursor()

nt = NetworkTable("WFO")

print("WFO,CNTY_HITS,CWA_HITS,ALL")
for wfo in nt.sts.keys():
    cursor.execute("""
    WITH dumps as (
        select (st_dumppoints(ST_Transform(geom, 2163))).* from sbw
        where wfo = %(wfo)s
        and phenomena in ('SV', 'TO')
        and status = 'NEW' and issue > '2007-10-01'),
    points as (
        SELECT path, geom from dumps),
    cbuf as (
        SELECT ugc, name,
        ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(
            st_transform(geom, 2163)),1)),2000.) as bgeom
        from ugcs where wfo = %(wfo)s
        and substr(ugc, 3, 1) = 'C' and end_ts is null),
    wbuf as (
        SELECT wfo,
        ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(
            st_transform(the_geom, 2163)),1)),2000.) as wgeom
        from cwa where wfo = %(wfo)s),
    agg as (
        select (path)[3] as pt, p.geom, c.name
        from points p LEFT JOIN cbuf c ON
        ST_Within(p.geom, c.bgeom) where (path)[3] != 1),
    agg2 as (
        select a.pt, a.name, c.wfo from agg a LEFT JOIN wbuf c ON
        ST_Within(a.geom, c.wgeom))

    select sum(case when name is not null then 1 else 0 end),
    sum(case when wfo is not null then 1 else 0 end), count(*) from agg2
    """, dict(wfo=wfo))

    if cursor.rowcount > 0:
        row = cursor.fetchone()
        print("%s,%s,%s,%s" % (wfo, row[0], row[1], row[2]))
