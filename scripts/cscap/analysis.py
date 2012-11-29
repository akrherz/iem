import iemplot
import network
import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()

nt = network.Table(("IACLIMATE", "MNCLIMATE", "NDCLIMATE", "SDCLIMATE",
 "NECLIMATE", "KSCLIMATE", "MOCLIMATE", "KYCLIMATE", "ILCLIMATE", "WICLIMATE",
 "INCLIMATE", "OHCLIMATE", "MICLIMATE"))

ccursor.execute("""
select march.station, march.avg - april.avg as diff from (select station, avg((high+low)/2.0) from alldata WHERE year = 2012 and month = 3 GROUP by station) as march, (select station, avg((high+low)/2.0) from alldata WHERE year = 2012 and month = 4 GROUP by station) as april WHERE march.station = april.station ORDER by diff DESC
""")

vals = []
lats = []
lons = []
for row in ccursor:
    station = row[0]
    if not nt.sts.has_key(station):
        continue
    vals.append( row[1] )
    lats.append( nt.sts[station]['lat'] )
    lons.append( nt.sts[station]['lon'] )
    
cfg = {'_title': "2012 March versus April Average Temperature",
       '_valid': '(preliminary data) Postive values are warmer March than April',
       'lbTitleString': 'F',
#'wkColorMap': 'ViBlGrWhYeOrRe',
'wkColorMap': 'BlWhRe',
 'cnLevelSelectionMode': 'ManualLevels',
  'cnLevelSpacingF'      : 1.0,
 'cnMinLevelValF'       : -8.0,
 'cnMaxLevelValF'       : 8.0,
       '_midwest': True}
tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)
iemplot.makefeature(tmpfp)
