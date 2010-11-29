# Process SCAN dataset

import urllib
import urllib2
import mx.DateTime
import mesonet
import access
import pg
iemdb = pg.connect("iem", "iemdb")
scandb = pg.connect("scan", "iemdb")

mapping = {
    'Site Id': {'iemvar': 'station', 'multiplier': 1},
    'Date': {'iemvar': '', 'multiplier': 1},
    'Time (CST)': {'iemvar': '', 'multiplier': 1},
    'Time (CDT)': {'iemvar': '', 'multiplier': 1},
   'PREC.I-1 (in)': {'iemvar': '', 'multiplier': 1},
   'PREC.I-2 (in)': {'iemvar': '', 'multiplier': 1},
   'TOBS.I-1 (degC)': {'iemvar': 'tmpc', 'multiplier': 1},
   'TMAX.H-1 (degC)':{'iemvar': '', 'multiplier': 1},
   'TMIN.H-1 (degC)': {'iemvar': '', 'multiplier': 1},
   'TAVG.H-1 (degC)':{'iemvar': '', 'multiplier': 1},
   'PRCP.H-1 (in)':{'iemvar': 'phour', 'multiplier': 1},
   'SMS.I-1:-2 (pct)':{'iemvar': 'c1smv', 'multiplier': 1},
   'SMS.I-1:-4 (pct)':{'iemvar': 'c2smv', 'multiplier': 1},
   'SMS.I-1:-8 (pct)':{'iemvar': 'c3smv', 'multiplier': 1},
   'SMS.I-1:-20 (pct)':{'iemvar': 'c4smv', 'multiplier': 1},
   'SMS.I-1:-40 (pct)':{'iemvar': 'c5smv', 'multiplier': 1},
   'STO.I-1:-2 (degC)':{'iemvar': 'c1tmpc', 'multiplier': 1},
   'STO.I-1:-4 (degC)':{'iemvar': 'c2tmpc', 'multiplier': 1},
   'STO.I-1:-8 (degC)':{'iemvar': 'c3tmpc', 'multiplier': 1},
   'STO.I-1:-20 (degC)':{'iemvar': 'c4tmpc', 'multiplier': 1},
   'STO.I-1:-40 (degC)':{'iemvar': 'c5tmpc', 'multiplier': 1},
   'STO.I-2:-2 (degC)':{'iemvar': '', 'multiplier': 1},
   'STO.I-2:-4 (degC)':{'iemvar': '', 'multiplier': 1},
   'STO.I-2:-8 (degC)':{'iemvar': '', 'multiplier': 1},
   'STO.I-2:-20 (degC)':{'iemvar': '', 'multiplier': 1},
   'STO.I-2:-40 (degC)':{'iemvar': '', 'multiplier': 1},
   'SAL.I-1:-2 (gram/l)':{'iemvar': '', 'multiplier': 1},
   'SAL.I-1:-4 (gram/l)':{'iemvar': '', 'multiplier': 1},
   'SAL.I-1:-8 (gram/l)':{'iemvar': '', 'multiplier': 1},
   'SAL.I-1:-20 (gram/l)':{'iemvar': '', 'multiplier': 1},
   'SAL.I-1:-40 (gram/l)':{'iemvar': '', 'multiplier': 1},
   'RDC.I-1:-2 (unitless)':{'iemvar': '', 'multiplier': 1},
   'RDC.I-1:-4 (unitless)':{'iemvar': '', 'multiplier': 1},
   'RDC.I-1:-8 (unitless)':{'iemvar': '', 'multiplier': 1},
   'RDC.I-1:-20 (unitless)':{'iemvar': '', 'multiplier': 1},
   'RDC.I-1:-40 (unitless)':{'iemvar': '', 'multiplier': 1},
   'BATT.I-1 (volt)':{'iemvar': '', 'multiplier': 1},
   'BATT.I-2 (volt)':{'iemvar': '', 'multiplier': 1},
   
   'WDIRV.H-1:144 (degree)':{'iemvar': 'drct', 'multiplier': 1},
   'WDIRV.H-1:101 (degree)':{'iemvar': 'drct', 'multiplier': 1},
   'WDIRV.H-1:120 (degree)':{'iemvar': 'drct', 'multiplier': 1},
   'WDIRV.H-1:140 (degree)':{'iemvar': 'drct', 'multiplier': 1},
   'WDIRV.H-1:117 (degree)':{'iemvar': 'drct', 'multiplier': 1},

   'WSPDX.H-1:144 (mph)':{'iemvar': 'gust', 'multiplier': 0.8689},
   'WSPDX.H-1:101 (mph)':{'iemvar': 'gust', 'multiplier': 0.8689},
   'WSPDX.H-1:120 (mph)':{'iemvar': 'gust', 'multiplier': 0.8689},
   'WSPDX.H-1:140 (mph)':{'iemvar': 'gust', 'multiplier': 0.8689},
   'WSPDX.H-1:117 (mph)':{'iemvar': 'gust', 'multiplier': 0.8689},
   
   'WSPDV.H-1:144 (mph)':{'iemvar': 'sknt', 'multiplier': 0.8689},
   'WSPDV.H-1:101 (mph)':{'iemvar': 'sknt', 'multiplier': 0.8689},
   'WSPDV.H-1:120 (mph)':{'iemvar': 'sknt', 'multiplier': 0.8689},
   'WSPDV.H-1:140 (mph)':{'iemvar': 'sknt', 'multiplier': 0.8689},
   'WSPDV.H-1:117 (mph)':{'iemvar': 'sknt', 'multiplier': 0.8689},
   
   'RHUM.I-1 (pct)':{'iemvar': 'relh', 'multiplier': 1},
   'PRES.I-1 (inch_Hg)':{'iemvar': 'pres', 'multiplier': 1},
   'SRADV.H-1 (watt/m2)':{'iemvar': 'srad', 'multiplier': 1},
   'DPTP.H-1 (degC)':{'iemvar': 'dwpc', 'multiplier': 1},
   'PVPV.H-1 (kPa)':{'iemvar': '', 'multiplier': 1},
   'RHUMN.H-1 (pct)':{'iemvar': '', 'multiplier': 1},
   'RHUMX.H-1 (pct)':{'iemvar': '', 'multiplier': 1},
   'SVPV.H-1 (kPa)':{'iemvar': '', 'multiplier': 1},
}

postvars = {
    'sitenum': '2031',
    'report': 'ALL',
    'timeseries': 'Hourly',
    'interval': 'DAY', # PST ?
    'format': 'copy',
   # 'site_name': 'Ames',
   # 'state_name': 'Iowa',
    'site_network': 'scan',
    'time_zone': 'CST',
}
URI = 'http://www.wcc.nrcs.usda.gov/nwcc/view'

def savedata( data , maxts ):
    """
    Save away our data into IEM Access
    """
    if data.has_key('Time (CST)'):
        tstr = "%s %s" % (data['Date'], data['Time (CST)'])
    else:
        tstr = "%s %s" % (data['Date'], data['Time (CDT)'])
    ts = mx.DateTime.strptime(tstr, '%Y-%m-%d %H:%M')
    id = "S%s" % (data['Site Id'],)
    
    if maxts[id] > ts:
        return
    iem = access.Ob(id, 'SCAN')
    iem.data['ts'] = ts
    iem.data['year'] = ts.year
    for key in data.keys():
        if mapping.has_key(key) and mapping[key]['iemvar'] != "":
            iem.data[ mapping[key]['iemvar'] ] = data[key]

    iem.data['valid'] = ts.strftime("%Y-%m-%d %H:%M")
    iem.data['tmpf'] = mesonet.c2f(iem.data['tmpc'])
    iem.data['dwpf'] = mesonet.c2f(iem.data['dwpc'])
    iem.data['c1tmpf'] = mesonet.c2f(iem.data['c1tmpc'])
    iem.data['c2tmpf'] = mesonet.c2f(iem.data['c2tmpc'])
    iem.data['c3tmpf'] = mesonet.c2f(iem.data['c3tmpc'])
    iem.data['c4tmpf'] = mesonet.c2f(iem.data['c4tmpc'])
    iem.data['c5tmpf'] = mesonet.c2f(iem.data['c5tmpc'])     

    iem.updateDatabase(iemdb)

    sql = """INSERT into t%(year)s_hourly (station, valid, tmpf, 
        dwpf, srad, 
         sknt, drct, relh, pres, c1tmpf, c2tmpf, c3tmpf, c4tmpf, 
         c5tmpf, 
         c1smv, c2smv, c3smv, c4smv, c5smv, phour) 
        VALUES 
        ('%(station)s', '%(valid)s', '%(tmpf)s', '%(dwpf)s',
         '%(srad)s','%(sknt)s',
        '%(drct)s', '%(relh)s', '%(pres)s', '%(c1tmpf)s', 
        '%(c2tmpf)s', 
        '%(c3tmpf)s', '%(c4tmpf)s', '%(c5tmpf)s', '%(c1smv)s',
         '%(c2smv)s', 
        '%(c3smv)s', '%(c4smv)s', '%(c5smv)s', '%(phour)s')
        """ % iem.data
    mydb.query(sql)

def load_times():
    """
    Load the latest ob times from the database
    """
    rs = iemdb.query("""SELECT station, valid from current
        WHERE network = 'SCAN'""").dictresult()
    d = {}
    for i in range(len(rs)):
        d[ rs[i]['station'] ] = mx.DateTime.strptime( 
                                            rs[i]['valid'][:16], '%Y-%m-%d %H:%M')
    return d

def main():
    maxts = load_times()
    for id in ['2068', '2031', '2047', '2001', '2004']:
        postvars['sitenum'] = id
        data = urllib.urlencode(postvars)
        req = urllib2.Request(URI, data)
        response = urllib2.urlopen(req)
        lines = response.readlines()
        cols = lines[1].split(",")
        data = {}
        for row in lines[2:]:
            if row.strip() == "":
                continue
            tokens = row.split(",")
            for col, token in zip(cols, tokens):
                if col.strip() == '':
                    continue
                col = col.replace('  (loam)', '').replace('  (silt)', '')
                data[col.strip()] = token
            savedata( data , maxts)
main()
