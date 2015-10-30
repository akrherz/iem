

# Iowa Road Conditions processing script
# daryl herzmann akrherz@iastate.edu  19 Nov 2009
# installed by Shane Searcy, ITO DMX, shane.searcy@noaa.gov
#
# REQUIRES: the 'mx' package installed (standard yum install mx)
#
# 1) Download file from website
# 2) Compare with old file to see if they are any different
# IF DIFFERENT
#   3) Replace Headers with NWS mandated stuff
#   4) Write file to hard drive
#   5) scp file to ls1-dmx:/data/Incoming for dissemination

HTTP_SRC = "http://ia.carsprogram.org/IAcarssegment/IA_road_conditions.txt"
#FINAL_LOCATION = "/data/Incoming/WAN_NWWSDSMSTOIA.dat"
FINAL_LOCATION = "/usr/local/utils/stoia/LOC_DSMSTOIA.dat"
LOG_FILENAME = "/usr/local/utils/stoia/STOIA_acquisition.log"
PREV_PRODUCT = "/usr/local/utils/stoia/prevSTOIA.txt"

import urllib2, logging, traceback, sys, os, tempfile, StringIO
import datetime
LOGFORMAT = "%(asctime)-15s:: %(message)s"
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,
                    format=LOGFORMAT)

def compare_product( newdata ):
    """
    Compares newly downloaded data with previously saved version
    @return boolean if the data is new!
    """
    if not os.path.isfile( PREV_PRODUCT ):
        logging.debug("Previous datafile %s not found" % (PREV_PRODUCT,))
        return True

    # Always send the 3:01 a.m. report
    now = datetime.datetime.now()
    if now.minute == 1 and now.hour == 3:
        return True

    # Make sure the product is complete...
    if newdata.find("800-762-3947") == -1:
        return False

    olddata = open( PREV_PRODUCT, 'r').read()
    if olddata != newdata:
        logging.debug("Datafile is new!")
        return True

    return False

def ship2ldad( data ):
    """
    Writes the data to a file for LDAD to then deal with
    """
    f = open ("/usr1/stoia/pre_ldad_STOIA.txt", 'w')
    f.write( data )
    f.close()

    os.system("sync")

    logging.debug("Shipping %s product to LDAD via scp" % (f.name,) )
    os.system("scp -q %s ldad@ls1-dmx.dmx.noaa.gov:%s" % (f.name, FINAL_LOCATION) )

def fix_header( data ):
    """
    Fixes the header the file has to make NWS protocols
    @return String fixed file
    """
    # Formulate the new header
    now = datetime.datetime.now()
    newdata = """

IOWA ROAD CONDITIONS
IOWA DEPARTMENT OF PUBLIC SAFETY
RELAYED BY THE NATIONAL WEATHER SERVICE DES MOINES IA
%s

""" % ((now.strftime("%-I%M %p CST %a %b %d %Y").upper()),)

    # Strip off everything before the first *
    return newdata + data[data.find("*"):]
    return newdata + data    
 
def save_data( data ):
    """
    Save the data in a file for future comparisons
    """
    f = open( PREV_PRODUCT , 'w')
    f.write( data )
    f.close()
    logging.debug("Saved downloaded data to %s" % (PREV_PRODUCT,))

logging.debug("_______________ Starting download")
try:
    data = urllib2.urlopen( HTTP_SRC ).read()
    data = data[data.find("*"):]

except:
    logging.error("Download Failure!, Abort")
    ebuf = StringIO.StringIO()
    traceback.print_exc(file=ebuf)
    ebuf.seek(0)
    logging.error( ebuf.read() )
    logging.debug("__ END")
    sys.exit()

logging.debug("Downloaded %s bytes" % (len(data),))

isnew = compare_product( data )

save_data(data)

if isnew:
    data = fix_header( data )
    ship2ldad( data )

logging.debug("__ END")
