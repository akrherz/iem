"""

select wfo, sum( case when (rtrim(substring(array_dims(regexp_split_to_array(svs,E'\001')),4),']')::int -1) is null then 1 else 0 end) :: numeric / count(*)::numeric * 100.0 from warnings where gtype = 'P' and phenomena in ('SV','TO') and significance = 'W' and issue > '2007-10-01' GROUP by wfo;

select wfo, sum(case when (expire - issue) > '59 minutes'::interval then 1 else 0 end)::numeric / count(*)::numeric * 100.0 from warnings where gtype = 'P' and phenomena = 'TO' and significance = 'W' and issue > '2007-10-01' GROUP by wfo;

select wfo, avg(area(transform(geom,2163))) / 1000000.0 from
    (select * from warnings_2007 WHERE issue > '2007-10-01' and
     phenomena IN ('SV','TO') and significance = 'W' and gtype = 'P'
   UNION
     select * from warnings_2008 WHERE issue < '2008-10-01' and
     phenomena IN ('SV','TO') and significance = 'W' and gtype = 'P') as foo
  GROUP by wfo;

load into today on mesonet db

select wfo, round(avg(c),2) from (select wfo, phenomena, eventid, extract(year from issue) as i, count(*) - 1 as c from sbw WHERE issue BETWEEN '2007-10-01' and '2008-10-01' and significance = 'W' and phenomena IN ('SV','TO') GROUP by wfo, phenomena, eventid, i) as foo GROUP by wfo ORDER by WFO ASC;

"""

from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']


rs = postgis.query("""
SELECT distinct wfo, ST_area(ST_transform(geom, 2163)) as a, 
ST_length(ST_transform( ST_exteriorring(ST_geometryn(geom,1)) ,2163)) as sz,
phenomena, eventid, issue from warnings WHERE gtype = 'P' 
and phenomena IN ('SV','TO') and issue > '2012-01-01'
"""  ).dictresult()

for i in range(len(rs)):
  sql = "select sum(ST_area(ST_transform(geom, 2163))) as a, count(*) as c from (\
         SELECT distinct ugc, geom from warnings_%s WHERE eventid = %s \
         and phenomena = '%s' and significance = 'W' and gtype = 'C' and \
         wfo = '%s') as foo" % (rs[i]['issue'][:4],
         rs[i]['eventid'], rs[i]['phenomena'], rs[i]['wfo'])
  rs2 = postgis.query(sql).dictresult()

  # Compute perimeter ratio
  sql = """SELECT sum(sz) as s from (
  SELECT ST_length(ST_transform(a,2163)) as sz from (
        select 
           ST_intersection(
      ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(ST_union(n.geom)),1)),0.02),
      ST_exteriorring(ST_geometryn(ST_multi(ST_union(w.geom)),1))
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
            WHERE not ST_isempty(a)) as foo""" % (rs[i]['issue'][:4], rs[i]['wfo'], rs[i]['phenomena'],\
  rs[i]['eventid'], rs[i]['issue'][:4], rs[i]['wfo'], rs[i]['phenomena'],  rs[i]['eventid'])
  try:
    rs3 = postgis.query(sql).dictresult()
  except:
    rs3 = [{'s':None},]

  print "%s,%s,%s,%s,%s,%s,%s,%s,%s" % (rs[i]['issue'][:4], rs[i]['wfo'], rs[i]['eventid'], \
         rs[i]['phenomena'], rs[i]['a'], rs2[0]['a'], rs2[0]['c'], \
         rs3[0]['s'], rs[i]['sz'])
