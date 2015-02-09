import psycopg2
IEM = psycopg2.connect(database='iem', host='iemdb', user='nobody')
icursor = IEM.cursor()

icursor.execute("""
with one as (select iemid, snowd from summary_2015 
 where snowd >= 0 and day = '2015-02-07'), 
two as (select iemid, max_tmpf from summary_2015 
 where max_tmpf > 0 and day = '2015-02-08' 
 and extract(hour from coop_valid) between 4 and 10), 
data as (SELECT o.iemid, o.snowd, t.max_tmpf from one o JOIN two t 
 ON (t.iemid = o.iemid)) 

 SELECT t.id, d.snowd, d.max_tmpf from data d JOIN stations t 
 on (t.iemid = d.iemid) WHERE t.network in ('IA_COOP', 'MN_COOP',
 'SD_COOP', 'NE_COOP', 'KS_COOP', 'MO_COOP', 'IL_COOP',
 'MI_COOP', 'WI_COOP') ORDER by max_tmpf DESC
""")
snowd = []; high = []
ia_snowd = []; ia_high = []
for row in icursor:
  if row[0][-2:] == 'I4':
    ia_snowd.append(row[1])
    ia_high.append(row[2])
  else:
    snowd.append(row[1])
    high.append(row[2])


import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(snowd, high, marker='o', color='b', label='Surrounding\nStates')
ax.scatter(ia_snowd, ia_high, marker='s', color='r', zorder=2, label='Iowa')
ax.set_xlim(-0.3,30)
ax.legend()
ax.set_xlabel('Morning Snow Depth [inch]')
ax.set_ylabel('Afternoon High Temperature [F]')
ax.set_title("7 February 2015: High Temperature  vs. Snow Depth\nNWS COOP Reports over upper Midwest")
ax.grid(True)

fig.savefig('test.png')
