# Need something to process the archived monthly RWIS file provided by Tina
"""
Site number,sensor ID,lane ID,local date/time,2-minute av speed,total
vol,normal vol,long vol,headway (null),occupancy,
"""

import glob
import os
import mx.DateTime
import StringIO
from pyIEM import mesonet
import iemdb
RWIS = iemdb.connect('rwis')
rcursor = RWIS.cursor()

def clean(v):
    if v.strip() == '':
        return '\N'
    return v

def dofiles(files):
    """
    Actually process a file please
    """
    ts0 = None
    data = {}
    for file in files:
        for line in open(file):
            if line.strip() == "":
                continue
            tokens = line.split(",")
            id = int(tokens[0]) - 512000
            if id < 0:
                continue
            nwsli = mesonet.RWISconvert['%02i' % (id,)]
            sensor_id = tokens[1]
            try:
                ts = mx.DateTime.strptime(tokens[2], '%m/%d/%Y %H:%M')
            except:
                print line
                continue
            if ts0 is None:
                ts0 = ts
            tmpf = clean( tokens[3] )
            if not data.has_key(ts):
                data[ts] = ['\N']*15
            data[ts][int(sensor_id)] = tmpf
    o = StringIO.StringIO()
    for ts in data.keys():       
        o.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (nwsli, 
                    ts.strftime("%Y-%m-%d %H:%M"), data[ts][0], data[ts][1], data[ts][2],
                    data[ts][3], data[ts][4], data[ts][5], data[ts][6], data[ts][7],
                    data[ts][8], data[ts][9], data[ts][10], data[ts][11], data[ts][12],
                    data[ts][13], data[ts][14]) )
    o.seek(0)
    if ts0 is None:
        return
    # Now we delete old obs
    rcursor.execute("""
    DELETE from t%s_soil WHERE station = '%s' and
    valid >= '%s' and valid < ('%s'::timestamp + '1 month'::interval)
    """ % (ts0.year, nwsli,  ts0.strftime('%Y-%m-01'),
           ts0.strftime('%Y-%m-01')))
    rcursor.copy_from(o, 't%s_soil' % (ts.year,))
    RWIS.commit()
    del o


def process_folder():
    """
    Do the necessary work to process the files in a folder
    """
    os.chdir('process')
    for id in mesonet.RWISconvert.keys():
        dofiles(glob.glob("export5120%s*sub*.csv" % (id,))) 
        
if __name__ == '__main__':
    process_folder()
    RWIS.close()