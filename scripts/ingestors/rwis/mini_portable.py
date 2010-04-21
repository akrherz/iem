# Process data from the mini and portables 

import mx.DateTime
from pyIEM import iemAccess
from pyIEM import iemAccessOb
from pyIEM import mesonet, tracker, stationTable
iemaccess = iemAccess.iemAccess()
st = stationTable.stationTable("/mesonet/TABLES/RWIS.stns")

lkp = {
'miniExportM1.csv': 'RAII4',
'miniExportM2.csv': 'RMYI4',
'portableExportP3.csv': 'RLMI4',
'portableExportPT.csv': 'ROCI4',
}

thres = mx.DateTime.now() - mx.DateTime.RelativeDateTime(minutes=180)

def processfile( fp ):
    o = open("/mesonet/data/incoming/rwis/%s" % (fp,), 'r').readlines()
    heading = o[0].split(",")
    cols = o[1].split(",")
    data = {}
    for i in range(len(heading)):
        if cols[i].strip() != "/":
            data[ heading[i].strip() ] = cols[i].strip()

    #print data
    nwsli = lkp[ fp ]
    iem = iemAccessOb.iemAccessOb(nwsli, 'IA_RWIS')
    ts = mx.DateTime.strptime(data['date_time'][:-6], '%Y-%m-%d %H:%M')
    if ts.year < 2010:
      print "BAD! timestamp", ts
      return
    iem.setObTime( ts )
    iem.ts = ts
    iem.load_and_compare(iemaccess)

    # IEM Tracker garbage
    if ts > thres:
        tracker.checkStation(st, nwsli, iem, "IA_RWIS", "iarwis", False)
    else: 
        tracker.doAlert(st, nwsli, iem, "IA_RWIS", "iarwis", False)


    if data.has_key('wind_speed') and data['wind_speed'] != '':
        iem.data['sknt'] = float( data['wind_speed'] ) * 1.17  # to knots
    if data.has_key('sub') and data['sub'] != '':
        iem.data['rwis_subf'] = float( data['sub'] )
    if data.has_key('air_temp') and data['air_temp'] != '':
        iem.data['tmpf'] = float( data['air_temp'] )
    if data.has_key('pave_temp') and data['pave_temp'] != '':
        iem.data['tsf0'] = float( data['pave_temp'] )
    if data.has_key('pave_temp2') and data['pave_temp2'] != '':
        iem.data['tsf1'] = float( data['pave_temp2'] )
    if data.has_key('press') and data['press'] != '':
        iem.data['alti'] = float( data['press'] )
    if data.has_key('RH') and data['RH'] != '':
        iem.data['dwpf'] = mesonet.dwpf(iem.data['tmpf'], float( data['RH'] ))
    if data.has_key('wind_dir') and data['wind_dir'] != '':
        iem.data['drct'] = float( data['wind_dir'] )
    iem.updateDatabase(iemaccess)

for k in lkp.keys():
    processfile( k )
