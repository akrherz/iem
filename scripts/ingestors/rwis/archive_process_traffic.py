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

def dofile(fp):
    """
    Actually process a file please
    """
    ts0 = None
    o = StringIO.StringIO()
    for line in open(fp):
        if line.strip() == "":
            continue
        tokens = line.replace('%','').replace('&nbsp;','').split(",")
        id = int(tokens[0]) - 512000
        nwsli = mesonet.RWISconvert['%02i' % (id,)]
        sensor_id = tokens[1]
        lane_id = tokens[2]
        ts = mx.DateTime.strptime(tokens[3], '%m/%d/%Y %H:%M')
        if ts0 is None:
            ts0 = ts
        sped = clean( tokens[4] )
        vol = clean( tokens[5] )
        norm_vol = clean( tokens[6] )
        
        long_vol = clean( tokens[7] )
        headway = clean( tokens[8] )
        occupancy = clean( tokens[9] )
        o.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (nwsli, 
                    ts.strftime("%Y-%m-%d %H:%M"), lane_id, sped, headway,
                    norm_vol, long_vol, occupancy) )
    o.seek(0)
    if ts0 is None:
        return
    # Now we delete old obs
    rcursor.execute("""
    DELETE from t%s_traffic WHERE station = '%s' and lane_id = %s and
    valid >= '%s' and valid < ('%s'::timestamp + '1 month'::interval)
    """ % (ts0.year, nwsli, lane_id, ts0.strftime('%Y-%m-01'),
           ts0.strftime('%Y-%m-01')))
    rcursor.copy_from(o, 't%s_traffic' % (ts.year,))
    RWIS.commit()
    del o


def process_folder():
    """
    Do the necessary work to process the files in a folder
    """
    os.chdir('process')
    for file in glob.glob("export*traffic*.csv"):
        dofile( file )
        
if __name__ == '__main__':
    process_folder()
    RWIS.close()