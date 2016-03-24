"""
with data as (select distinct substr(ugc, 1, 2) as state, 
  generate_series(issue, expire, '1 minute'::interval) as ts from warnings
  where phenomena = 'TO' and significance = 'W'),
data2 as (select distinct substr(ugc, 1, 2) as state,
  generate_series(issue, expire, '1 minute'::interval) as ts from warnings
  where phenomena in('BZ', 'WS') and significance = 'W'),
data3 as (SELECT o.state, o.ts from data2 o JOIN data t on (o.state = t.state
  and o.ts = t.ts))
select distinct state, date(ts) from data3 ORDER by date ASC;"""

txt = """ MI    | 2005-11-15
 KS    | 2005-11-27
 TN    | 2005-11-28
 CA    | 2005-12-31
 CA    | 2006-01-02
 IL    | 2006-02-16
 CA    | 2006-02-28
 CA    | 2006-03-03
 IL    | 2006-03-09
 IL    | 2006-03-11
 IA    | 2006-03-12
 WI    | 2006-03-12
 IL    | 2006-03-12
 IL    | 2006-03-13
 CA    | 2006-03-14
 OK    | 2006-03-20
 CA    | 2006-03-28
 TX    | 2006-11-29
 MO    | 2006-11-29
 TX    | 2006-12-29
 KS    | 2007-02-24
 CO    | 2007-03-24
 CO    | 2007-03-28
 TX    | 2007-04-13
 NC    | 2007-04-15
 CO    | 2007-04-24
 CO    | 2007-05-04
 CO    | 2007-05-05
 MI    | 2008-01-07
 WA    | 2008-01-10
 CA    | 2008-01-24
 CA    | 2008-01-25
 IN    | 2008-01-29
 IL    | 2008-01-29
 IL    | 2008-02-05
 MO    | 2008-02-05
 AR    | 2008-03-03
 TX    | 2008-03-06
 MI    | 2008-04-11
 SD    | 2008-05-01
 CO    | 2008-05-22
 WY    | 2008-05-22
 CO    | 2008-05-23
 CA    | 2008-12-15
 MO    | 2008-12-27
 CO    | 2009-03-07
 NE    | 2009-03-23
 SD    | 2009-03-23
 TX    | 2009-03-26
 TX    | 2009-03-27
 OK    | 2009-03-27
 NE    | 2009-04-04
 CO    | 2009-04-17
 TX    | 2009-12-23
 AR    | 2009-12-24
 TX    | 2009-12-24
 CA    | 2010-01-18
 CA    | 2010-01-19
 CA    | 2010-01-20
 CA    | 2010-01-21
 AZ    | 2010-01-21
 TX    | 2010-01-28
 TX    | 2010-01-29
 TX    | 2010-03-25
 CO    | 2010-04-22
 CO    | 2010-04-23
 OR    | 2010-12-14
 CA    | 2011-02-19
 MO    | 2011-02-24
 VA    | 2011-03-10
 CA    | 2011-03-18
 PA    | 2011-03-23
 CO    | 2011-05-11
 CA    | 2011-05-17
 CO    | 2011-05-18
 CO    | 2011-05-19
 CO    | 2011-10-07
 TX    | 2011-12-20
 TX    | 2012-01-09
 CA    | 2012-10-22
 MO    | 2012-12-19
 TX    | 2012-12-25
 MO    | 2013-01-29
 CA    | 2013-02-19
 TX    | 2013-02-21
 CO    | 2013-04-08
 NE    | 2013-04-08
 SD    | 2013-10-04
 NE    | 2013-10-04
 NC    | 2013-11-26
 CA    | 2014-02-28
 CA    | 2014-03-01
 CA    | 2014-03-26
 CA    | 2014-03-29
 SD    | 2014-03-31
 MN    | 2014-03-31
 MT    | 2014-06-17
 WA    | 2014-11-23
 TX    | 2014-12-27
 TX    | 2015-01-03
 CA    | 2015-04-07
 CO    | 2015-04-16
 CO    | 2015-04-17
 CO    | 2015-04-18
 NE    | 2015-05-09
 CO    | 2015-05-09
 SD    | 2015-05-10
 CO    | 2015-05-15
 CO    | 2015-05-19
 CA    | 2015-11-09
 NE    | 2015-11-11
 CA    | 2015-12-24
 OK    | 2015-12-26
 TX    | 2015-12-26
 OK    | 2015-12-27
 TX    | 2015-12-27
 CA    | 2016-01-06
 NC    | 2016-02-16"""
from pyiem.plot import MapPlot
import pandas as pd
import StringIO
import matplotlib.pyplot as plt

df = pd.read_csv(StringIO.StringIO(txt.replace(" ", "")), sep='|')
df.columns = ['states', 'date']
df2 = df.groupby('states').count()
data = {}
for i, row in df2.iterrows():
  data[i] = row['date']
print data

m = MapPlot(sector='conus', title='Days with Tornado Warning & Winter Storm or Blizzard Warning', subtitle='1 Oct 2005 - 23 Mar 2016 :: # of Dates with both alerts active within the same state at the same time', axisbg='white')

cmap = plt.get_cmap('jet')
cmap.set_over('black')
cmap.set_under('white')
m.fill_states(data, bins=[0, 1, 2, 3, 4, 5, 7, 10, 15, 20, 30], units='count', ilabel=True, cmap=cmap)

m.postprocess(filename='states.png')
