import psycopg2

pgconn = psycopg2.connect(database='postgis', host='localhost', port=5555,
                          user='nobody')
cursor = pgconn.cursor()

cursor.execute("""
    WITH dumps as (
        select (st_dumppoints(geom)).* from sbw_2016 where wfo = 'DMX'
        and phenomena = 'SV' and status = 'NEW'),
    points as (
        SELECT path, geom from dumps),
    cbuf as (
        SELECT ugc, name,
        ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(
            geom),1)),0.02) as bgeom
        from ugcs where wfo = 'DMX'
        and substr(ugc, 3, 1) = 'C' and end_ts is null),
    agg as (
        select (path)[3] as pt, c.name from points p LEFT JOIN cbuf c ON
        ST_Within(p.geom, c.bgeom) where (path)[3] != 1)
    select sum(case when name is null then 1 else 0 end), count(*) from agg
    """)

print cursor.fetchall()
