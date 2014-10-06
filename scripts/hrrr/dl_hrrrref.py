"""
Download 1000 ft reflectivity from the NCEP HRRR
"""
import sys
import datetime
import urllib2

def run(valid):
    """ run for this valid time! """
    output = open("/tmp/ncep_hrrr_%s.grib2" % (valid.strftime("%Y%m%d%H"),),
                  'wb')
    for hr in range(0,16):
        shr = "%02i" % (hr,)
        uri = valid.strftime(("http://www.ftp.ncep.noaa.gov/data/nccf/"
            +"nonoperational/com/hrrr/prod/hrrr.%Y%m%d/hrrr.t%Hz.wrfsubhf"+shr
            +".grib2.idx"))
        data = urllib2.urlopen(uri)

        offsets = []
        neednext = False
        for line in data:
            tokens = line.split(":")
            if neednext:
                offsets[-1].append( int(tokens[1]))
                neednext = False
            if tokens[3] == 'REFD' and tokens[4] == '1000 m above ground':
                offsets.append( [int(tokens[1])] )
                neednext = True

        req = urllib2.Request(uri[:-4])
                              
        for pr in offsets:
            req.headers['Range'] = 'bytes=%s-%s' % (pr[0], pr[1])
            f = urllib2.urlopen(req)
            output.write( f.read() )

    output.close()
    
def main():
    """ Go Main Go """
    valid = datetime.datetime( int(sys.argv[1]), int(sys.argv[2]),
                               int(sys.argv[3]), int(sys.argv[4]))
    run(valid)
    
if __name__ == '__main__':
    # do main
    main()