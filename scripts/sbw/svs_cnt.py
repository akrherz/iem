from pyIEM import iemdb
i = iemdb.iemdb()
postgis = i['postgis']

data = {}

for phenom in ['TO','SV']:
  rs = postgis.query("""
SELECT
  wfo, count(*) as tot,
  sum(CASE WHEN svscnt is Null THEN 1 ELSE 0 END) as zerocnt,
  sum(svscnt) as sum
FROM (
select
  wfo, eventid,
  rtrim(substring(array_dims(regexp_split_to_array(svs,'\001')),4),']')::int -1  as svscnt
from warnings_2008
WHERE 
 phenomena = '%s' and gtype = 'P') as foo
GROUP by wfo""" % (phenom,)).dictresult()
  for i in range(len(rs)):
    wfo = rs[i]['wfo']
    cnt = rs[i]['tot']
    avg = rs[i]['sum'] / float(cnt)
    zcnt = rs[i]['zerocnt']
    if not data.has_key(wfo):
      data[wfo] = {'TO': {'cnt': 0, 'avg': 0, 'zcnt': 0},
                   'SV': {'cnt': 0, 'avg': 0, 'zcnt': 0} }
    data[wfo][phenom]['cnt'] = cnt
    data[wfo][phenom]['avg'] = avg
    data[wfo][phenom]['zcnt'] = zcnt

for wfo in data.keys():
  print "%s,%s,%.1f,%s,%s,%.1f,%s" % (wfo,
    data[wfo]['SV']['cnt'], data[wfo]['SV']['avg'], data[wfo]['SV']['zcnt'],
    data[wfo]['TO']['cnt'], data[wfo]['TO']['avg'], data[wfo]['TO']['zcnt'])
