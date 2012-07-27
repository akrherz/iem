import iemplot
import iemdb
import network
import mx.DateTime
nt = network.Table("IACLIMATE")
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

ccursor.execute("""
select obs.station, max(obs.day)  from (select station, sday, day, high from alldata_ia ) as obs, (select station, high, to_char(valid, 'mmdd') as sday from climate) as climate WHERE climate.station = obs.station and climate.sday = obs.sday and obs.high < climate.high GROUP by obs.station ORDER by max
""")
now = mx.DateTime.now()
lats = []
lons = []
vals = []
for row in ccursor:
    if not nt.sts.has_key(row[0]) or row[0][2] == 'C' or row[0][3:] == '0000':
        continue
    lats.append( nt.sts[row[0]]['lat'])
    lons.append( nt.sts[row[0]]['lon'])
    ts = mx.DateTime.strptime(str(row[1]), '%Y-%m-%d')
    vals.append( (now - ts).days)
    
cfg = {'lbTitleString': 'days',
       '_title': 'blah',
       '_showvalues': True,
       '_format': '%.0f'}

tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)