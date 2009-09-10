# Compute number of cyles per season 

def write(mydb, rs, stationID, _REPORTID):
  import constants, mx.DateTime
  s = constants.startts(stationID)
  e = constants._ENDTS
  YEARS = e.year - s.year + 1

  out = open("reports/%s_%s.txt" % (stationID, _REPORTID), 'w')
  constants.writeheader(out, stationID)

  out.write("""# SEASONAL TEMPERATURE CYCLES PER YEAR
# 1 CYCLE IS A TEMPERATURE VARIATION FROM A VALUE BELOW A THRESHOLD 
#   TO A VALUE EXCEEDING A THRESHOLD.  THINK OF IT AS FREEZE/THAW CYCLES
#  FIRST DATA COLUMN WOULD BE FOR CYCLES EXCEEDING 26 AND 38 DEGREES F
THRES  26-38   26-38   24-40   24-40   20-44   20-44   14-50   14-50
YEAR   SPRING  FALL    SPRING  FALL    SPRING  FALL    SPRING  FALL
""")

  data = {}
  for yr in range(constants.startyear(stationID), constants._ENDYEAR):
    data[yr] = {'26s':0, '26f': 0, 
                '24s':0, '24f': 0,
                '20s':0, '20f': 0,
                '14s':0, '14f': 0}
 
  prs = [[26,38], [24,40], [20,44], [14,50]]
  
  cycPos = {'26s': -1, '24s': -1, '20s': -1, '14s': -1}
 
  for i in range(len(rs)):
    ts = mx.DateTime.strptime(rs[i]["day"], "%Y-%m-%d")
    high = int(rs[i]['high'])
    low = int(rs[i]['low'])

    for pr in prs:
      l,u = pr
      key = '%ss'%(l,)
      ckey = '%ss'%(l,)
      if (ts.month >= 7):
        ckey = '%sf'%(l,)
      
      # cycles lower
      if (cycPos[key] == 1 and low < l):
        #print 'Cycled lower', low, ts
        cycPos[key] = -1
        data[ts.year][ckey] += 0.5

      # cycled higher
      if (cycPos[key] == -1 and high > u):
        #print 'Cycled higher', high, ts
        cycPos[key] = 1
        data[ts.year][ckey] += 0.5

  s26 = 0
  f26 = 0
  s24 = 0
  f24 = 0
  s20 = 0
  f20 = 0
  s14 = 0
  f14 = 0
  for yr in range(constants.startyear(stationID), constants._ENDYEAR):
    s26 += data[yr]['26s']
    f26 += data[yr]['26f']
    s24 += data[yr]['24s']
    f24 += data[yr]['24f']
    s20 += data[yr]['20s']
    f20 += data[yr]['20f']
    s14 += data[yr]['14s']
    f14 += data[yr]['14f']
    out.write("%s   %-8i%-8i%-8i%-8i%-8i%-8i%-8i%-8i\n" % (yr,data[yr]['26s'],\
        data[yr]['26f'],data[yr]['24s'],data[yr]['24f'],\
        data[yr]['20s'],data[yr]['20f'],data[yr]['14s'],data[yr]['14f'] ))

  out.write("AVG    %-8.1f%-8.1f%-8.1f%-8.1f%-8.1f%-8.1f%-8.1f%-8.1f\n" % (s26/YEARS, f26/YEARS, s24/YEARS, f24/YEARS, s20/YEARS, f20/YEARS, s14/YEARS, f14/YEARS) )

  out.close()
