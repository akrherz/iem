# 

import sys, os
import iemplot

import mx.DateTime

import iemdb
COOP = iemdb.connect('coop', bypass=True)
ccursor = COOP.cursor()
MESOSITE = iemdb.connect('mesosite', bypass=True)
mcursor = MESOSITE.cursor()

def doit():
    # Build list of sites we care about
    care = []
    data = {}
    ccursor.execute("""SELECT distinct stationid from alldata 
    where year = 1951 and year < 2010 and stationid != 'ia0000' """)
    for row in ccursor:
        care.append( row[0] )
        data[row[0]] = 0
    
    sts = mx.DateTime.DateTime(1951,1,1)
    ets = mx.DateTime.DateTime(2010,1,1)
    interval = mx.DateTime.RelativeDateTime(days=1)
    now = sts
    
    sql = """SELECT stationid, precip from alldata where
        day = %%s and stationid in %s and precip > 0.05 
        ORDER by precip DESC""" % (tuple(care),)
    events = 0.
    while now < ets:
        ccursor.execute(sql, (now.strftime("%Y-%m-%d"), ))
        high = None
        if row is not None:
            events += 1.
            for row in ccursor:
                if high is None:
                    high = row[1]
                if high == row[1]:
                    data[row[0]] += 1
                else:
                    break
        now += interval
    return data, events
 
#data, events = doit()
#print data, events
# precip
data = {'ia7726': 152, 'ia0753': 150, 'ia0112': 106, 'ia1063': 289, 'ia5086': 126, 'ia5837': 134, 'ia8806': 74, 'ia0200': 57, 'ia6327': 124, 'ia7842': 229, 'ia7844': 214, 'ia1962': 129, 'ia7312': 89, 'ia5123': 88, 'ia9067': 123, 'ia8296': 71, 'ia8755': 237, 'ia4049': 97, 'ia1277': 106, 'ia4585': 297, 'ia4228': 62, 'ia0213': 112, 'ia4502': 81, 'ia5230': 124, 'ia5235': 273, 'ia3007': 414, 'ia2789': 153, 'ia3718': 176, 'ia5131': 191, 'ia0364': 191, 'ia6800': 129, 'ia7979': 75, 'ia3980': 98, 'ia0133': 98, 'ia4038': 85, 'ia6200': 193, 'ia2203': 189, 'ia2689': 117, 'ia3487': 63, 'ia1354': 170, 'ia4101': 71, 'ia8339': 115, 'ia2724': 198, 'ia2864': 138, 'ia1635': 208, 'ia7613': 126, 'ia3438': 70, 'ia5769': 130, 'ia5493': 160, 'ia9132': 67, 'ia4735': 107, 'ia6940': 143, 'ia3632': 81, 'ia2999': 85, 'ia5796': 168, 'ia5952': 163, 'ia2977': 144, 'ia6103': 177, 'ia3584': 80, 'ia2110': 180, 'ia0157': 147, 'ia3509': 83, 'ia7594': 102, 'ia8568': 88, 'ia1233': 128, 'ia1442': 59, 'ia1402': 69, 'ia0149': 26, 'ia1833': 105, 'ia4894': 131, 'ia0923': 136, 'ia1394': 126, 'ia4142': 75, 'ia0807': 89, 'ia3517': 147, 'ia8706': 173, 'ia7678': 142, 'ia7161': 72, 'ia8266': 196, 'ia1731': 140, 'ia0241': 78, 'ia1533': 160, 'ia4705': 348, 'ia6316': 140, 'ia7664': 158, 'ia7708': 389, 'ia5992': 86, 'ia0385': 88, 'ia6243': 98, 'ia7669': 205, 'ia2171': 75, 'ia2364': 175, 'ia2573': 73, 'ia1319': 111, 'ia4063': 58, 'ia4389': 156, 'ia1541': 73, 'ia9999': 2, 'ia1257': 106, 'ia4381': 513, 'ia0608': 191, 'ia6389': 198, 'ia0600': 90, 'ia6151': 84, 'ia3473': 86, 'ia6305': 139, 'ia5198': 74, 'ia1954': 203, 'ia7147': 155, 'ia8688': 89, 'ia6566': 45, 'ia3290': 173, 'ia6719': 86, 'ia0576': 200}
events = 21550.0
# lows
#data = {'ia7726': 374, 'ia0753': 34, 'ia0112': 6, 'ia1063': 8, 'ia5086': 723, 'ia5837': 26, 'ia8806': 92, 'ia0200': 12, 'ia6327': 32, 'ia7842': 1302, 'ia7844': 977, 'ia1962': 92, 'ia7312': 132, 'ia5123': 162, 'ia9067': 76, 'ia8296': 245, 'ia8755': 726, 'ia4049': 406, 'ia1277': 95, 'ia4585': 5, 'ia4228': 20, 'ia0213': 717, 'ia4502': 21, 'ia5230': 357, 'ia5235': 765, 'ia3007': 69, 'ia2789': 21, 'ia3718': 664, 'ia5131': 428, 'ia0364': 699, 'ia6800': 667, 'ia7979': 615, 'ia3980': 156, 'ia0133': 207, 'ia4038': 247, 'ia6200': 323, 'ia2203': 3, 'ia2689': 139, 'ia3487': 239, 'ia1354': 31, 'ia4101': 75, 'ia8339': 183, 'ia2724': 654, 'ia2864': 1028, 'ia1635': 43, 'ia7613': 43, 'ia3438': 56, 'ia5769': 60, 'ia5493': 884, 'ia9132': 106, 'ia4735': 534, 'ia6940': 68, 'ia3632': 37, 'ia2999': 55, 'ia5796': 33, 'ia5952': 197, 'ia2977': 410, 'ia6103': 469, 'ia3584': 174, 'ia2110': 860, 'ia0157': 70, 'ia3509': 279, 'ia7594': 1215, 'ia8568': 91, 'ia1233': 456, 'ia1442': 690, 'ia1402': 104, 'ia0149': 12, 'ia1833': 212, 'ia4894': 69, 'ia0923': 281, 'ia1394': 343, 'ia4142': 128, 'ia0807': 288, 'ia3517': 58, 'ia8706': 260, 'ia7678': 60, 'ia7161': 32, 'ia8266': 222, 'ia1731': 61, 'ia0241': 35, 'ia1533': 132, 'ia4705': 53, 'ia6316': 74, 'ia7664': 2280, 'ia7708': 352, 'ia5992': 52, 'ia0385': 331, 'ia6243': 151, 'ia7669': 23, 'ia2171': 69, 'ia2364': 70, 'ia2573': 68, 'ia1319': 13, 'ia4063': 115, 'ia4389': 67, 'ia1541': 275, 'ia9999': 0, 'ia1257': 539, 'ia4381': 8, 'ia0608': 569, 'ia6389': 19, 'ia0600': 58, 'ia6151': 242,  'ia6305': 146, 'ia5198': 129, 'ia1954': 1873, 'ia7147': 834, 'ia8688': 24, 'ia6566': 59, 'ia3290': 145, 'ia6719': 267, 'ia0576': 72}
# highs   
#data = {'ia7726': 175, 'ia0753': 338, 'ia0112': 264, 'ia1063': 563, 'ia5086': 96, 'ia5837': 427, 'ia8806': 49, 'ia0200': 16, 'ia6327': 189, 'ia7842': 230, 'ia7844': 167, 'ia1962': 141, 'ia7312': 211, 'ia5123': 157, 'ia9067': 165, 'ia8296': 106, 'ia8755': 27, 'ia4049': 122, 'ia1277': 39, 'ia4585': 312, 'ia4228': 268, 'ia0213': 55, 'ia4502': 204, 'ia5230': 49, 'ia5235': 68, 'ia3007': 2135, 'ia2789': 286, 'ia3718': 597, 'ia5131': 127, 'ia0364': 425, 'ia6800': 94, 'ia7979': 73, 'ia3980': 98, 'ia0133': 79, 'ia4038': 109, 'ia6200': 19, 'ia2203': 223, 'ia2689': 97, 'ia3487': 30, 'ia1354': 322, 'ia4101': 282, 'ia8339': 27, 'ia2724': 94, 'ia2864': 15, 'ia1635': 273, 'ia7613': 1867, 'ia3438': 114, 'ia5769': 289, 'ia5493': 40, 'ia9132': 108, 'ia4735': 597, 'ia6940': 1133, 'ia3632': 109, 'ia2999': 104, 'ia5796': 237, 'ia5952': 10, 'ia2977': 54, 'ia6103': 32, 'ia3584': 40, 'ia2110': 63, 'ia0157': 81, 'ia3509': 316, 'ia7594': 84, 'ia8568': 48, 'ia1233': 209, 'ia1442': 171, 'ia1402': 31, 'ia0149': 27, 'ia1833': 539, 'ia4894': 582, 'ia0923': 90, 'ia1394': 202, 'ia4142': 76, 'ia0807': 221, 'ia3517': 132, 'ia8706': 142, 'ia7678': 343, 'ia7161': 48, 'ia8266': 335, 'ia1731': 378, 'ia0241': 193, 'ia1533': 430, 'ia4705': 441, 'ia6316': 260, 'ia7664': 60, 'ia7708': 1632, 'ia5992': 189, 'ia0385': 129, 'ia6243': 1128, 'ia7669': 1846, 'ia2171': 40, 'ia2364': 214, 'ia2573': 79, 'ia1319': 63, 'ia4063': 248, 'ia4389': 1480, 'ia1541': 47, 'ia1257': 129, 'ia4381': 2355, 'ia0608': 260, 'ia6389': 125, 'ia0600': 51, 'ia6151': 107, 'ia3473': 95, 'ia6305': 18, 'ia5198': 78, 'ia1954': 31, 'ia7147': 601, 'ia8688': 264, 'ia6566': 89, 'ia3290': 1780, 'ia6719': 223, 'ia0576': 700}
vals = []
lats = []
lons = []
for id in data.keys():
   
    mcursor.execute("""SELECT x(geom) as lon, y(geom) as lat from stations 
    WHERE id = %s""", (id.upper(),))
    row = mcursor.fetchone()
    if row is not None:
        vals.append( data[id] / events * 100.)
        lats.append( row[1] )
        lons.append( row[0] )

cfg = {
 'wkColorMap': 'BlAqGrYeOrRe',
 'nglSpreadColorStart': -1,
 'nglSpreadColorEnd': 2,
 '_title'             : "Frequency of site having largest daily precipitation [ties shared]",
 '_valid'             : "[1951-2009] based on long term sites",
 '_showvalues'        : True,
 '_format'            : '%.1f',
 'lbTitleString'      : "[%]",

}
# Generates tmp.ps
fp = iemplot.simple_contour(lons, lats, vals, cfg)

iemplot.makefeature(fp)
#iemplot.postprocess(fp, "")
