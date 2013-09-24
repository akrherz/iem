import psycopg2

ASOS = psycopg2.connect(database='asos', host='iemdb', user='nobody')
cursor = ASOS.cursor()

cursor.execute("""
 SELECT doy, sum(case when t = 0 and d = 0 and c = 0 then 1 else 0 end), count(*)
 from
  (SELECT extract(year from valid) as yr, extract(doy from valid) as doy,
  max(case when tmpf < 69.5 or tmpf >= 79.5 then 1 else 0 end) as t,
  max(case when dwpf >= 59.5 then 1 else 0 end) as d,
  max(case when 'OVC' in (skyc1,skyc2,skyc3,skyc4) or 
                'BRK' in (skyc1,skyc2,skyc3,skyc4) then 1 else 0 end) as c
  from alldata where station = 'DSM' 
  and extract(hour from valid) between 12 and 17 GROUP by yr, doy) as foo
  GROUP by doy ORDER by doy ASC
""")

doy = []
freq = []
for row in cursor:
    doy.append( row[0] )
    freq.append( row[1] / float(row[2]) * 100.0)
    
import matplotlib.pyplot as plt

(fig, ax) = plt.subplots(1,1)

ax.bar(doy, freq, fc='b', ec='b')
ax.grid(True)
ax.set_xticks( (1,32,60,91,121,152,182,213,244,274,305,335,365) )
ax.set_xticklabels( ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec') )
ax.set_title("1933-2012 Des Moines 12 PM - 5 PM Great Weather\nTemperature in 70s$^\circ$F, mostly clear, Dew Point below 60$^\circ$F")
ax.set_ylabel("Frequency [%]")
ax.set_xlabel("Day of Year")
fig.savefig('test.ps')
import iemplot
iemplot.makefeature('test')