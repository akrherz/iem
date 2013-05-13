import iemdb
import iemplot
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()
import network
nt = network.Table(('IA_ASOS','MO_ASOS','IL_ASOS', 'ND_ASOS', 'AWOS',
          'WI_ASOS','MN_ASOS', 'SD_ASOS', 'NE_ASOS', 'KS_ASOS',
          'IN_ASOS','KY_ASOS','OH_ASOS','MI_ASOS'))


icursor.execute("""
select after.id, after.max - before.max as diff from (select id, max(max_tmpf) from summary_2013 s JOIN stations t on (t.iemid = s.iemid) WHERE t.network ~* 'ASOS' and t.country = 'US' and t.state in ('IA','MN','WI','ND','SD','NE','KS','MO','IL','MI','IN','OH','KY') and day < '2013-04-26' GROUp by id) as before, (select id, max(max_tmpf) from summary_2013 s JOIN stations t on (t.iemid = s.iemid) WHERE t.network ~* 'ASOS' and t.state in ('IA','MN','WI','ND','SD','NE','KS','MO','IL','MI','IN','OH','KY') and day = '2013-04-26' GROUp by id) as after WHERE before.id = after.id ORDER by diff DESC
""")

lons = []
lats = []
vals = []
for row in icursor:
  if not nt.sts.has_key(row[0]) or row[0] in ('UNR','29G'):
    continue 
  if row[1] > -1 and row[1] < 1:
    continue
  if row[1] > -40:
    lons.append( nt.sts[ row[0] ]['lon'] )
    lats.append( nt.sts[ row[0] ]['lat'] )
    vals.append( row[1] )

cfg = {
  'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': 2,
 'nglSpreadColorEnd'  : -1,
 'cnLevelSelectionMode': 'ManualLevels',
  'cnLevelSpacingF'      : 4.0,
 'cnMinLevelValF'       : -32,
 'cnMaxLevelValF'       : 32,
 '_title'             : "High Temperature on 26 April 2013 vs Previous Highest for Year",
 '_showvalues'        : False,
 '_format'            : '%.0f',
 '_midwest' : True,
 'lbTitleString'      : "F",
}

tmpfp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.makefeature(tmpfp)
