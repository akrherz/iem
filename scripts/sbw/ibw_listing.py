"""
Wants:
  IBW tags of 2.75" Hail and/or 80+ MPH  (either initial and/or followups)

  - number of reports that verified the criterion
  - initial + followup hail and wind tags
  - where within the warning did the big LSRs happen
"""
import psycopg2
import pandas as pd
from pandas.io.sql import read_sql

pgconn = psycopg2.connect(database='postgis', host='iemdb', user='nobody')
cursor = pgconn.cursor()

# Get events for consideration
df = read_sql("""
  select wfo, phenomena, eventid,
  extract(year from polygon_begin)::numeric as year,
  max(case when status = 'NEW' then hailtag else 0 end) as init_hailtag,
  max(case when status = 'NEW' then windtag else 0 end) as init_windtag,
  max(hailtag) as max_hailtag, max(windtag) as max_windtag from sbw
  where hailtag >= 2.75 or windtag >= 80
  GROUP by wfo, phenomena, eventid, year
  ORDER by year, wfo, eventid
""", pgconn, index_col=None)
df['max_hail_report'] = None
df['max_wind_report'] = None
df['hail_reports'] = 0
df['wind_reports'] = 0

ws = []
for i, row in df.iterrows():
    # Get the polygon history for this warning
    sbwtable = "sbw_%i" % (row['year'], )
    lsrtable = "lsrs_%i" % (row['year'], )
    warndf = read_sql("""
    SELECT row_number() over(ORDER by polygon_begin ASC) as sequence,
    wfo, eventid, phenomena,
    extract(year from polygon_begin)::numeric as year, polygon_begin,
    polygon_end, status, windtag, hailtag,
    ST_asText(geom) as geomtext from """ + sbwtable + """ WHERE wfo = %s
    and eventid = %s and phenomena = %s and significance = %s
    and status != 'EXP' ORDER by
    polygon_begin
    """, pgconn, params=(row['wfo'], row['eventid'], row['phenomena'],
                         'W'), index_col=None)
    warndf['max_hail_report'] = None
    warndf['max_wind_report'] = None
    warndf['hail_reports'] = 0
    warndf['wind_reports'] = 0
    for j, wrow in warndf.iterrows():
        # Get LSRs
        lsrdf = read_sql("""
        SELECT distinct city, valid, type, magnitude
        from """ + lsrtable + """ WHERE valid >= %s and
        valid < %s and wfo = %s and type in ('H', 'G')
        and ST_Contains(ST_SetSrid(ST_GeometryFromText(%s), 4326), geom)
        """, pgconn, params=(wrow['polygon_begin'], wrow['polygon_end'],
                             row['wfo'], wrow['geomtext']), index_col=None)
        if len(lsrdf.index) == 0:
            continue
        g = lsrdf[lsrdf['type'] == 'G']
        h = lsrdf[lsrdf['type'] == 'H']
        if len(g.index) > 0:
            warndf.at[j, 'wind_reports'] = len(g.index)
            warndf.at[j, 'max_wind_report'] = g['magnitude'].max()
        if len(h.index) > 0:
            warndf.at[j, 'hail_reports'] = len(h.index)
            warndf.at[j, 'max_hail_report'] = h['magnitude'].max()
    del warndf['geomtext']
    ws.append(warndf)
    df.at[i, 'wind_reports'] = warndf['wind_reports'].sum()
    df.at[i, 'hail_reports'] = warndf['hail_reports'].sum()
    df.at[i, 'max_wind_report'] = warndf['max_wind_report'].max()
    df.at[i, 'max_hail_report'] = warndf['max_hail_report'].max()

writer = pd.ExcelWriter('ibwlisting.xlsx', options={'remove_timezone': True})
df.to_excel(writer, 'Overview', index=False)
w = pd.concat(ws)
w.to_excel(writer, 'By Polygon', index=False)
writer.save()
