"""
Drive the reprocessing of the MWcomp plot.  We are doing this since our
data archives have more data than the stuff I previously got from NSSL

$Id: $:
"""
import mx.DateTime
import subprocess
import iemdb
ASOS = iemdb.connect('asos', bypass=True)
acursor = ASOS.cursor()

min10 = mx.DateTime.RelativeDateTime(minutes=10)

def metar_extract( now ):
    """
    Giveme a METAR file with the data we have in the coffers
    """
    acursor.execute("""
    SELECT metar from t%s WHERE valid BETWEEN '%s+00' and '%s+00' 
    and metar is not null
    """ % (now.year, 
           (now - min10).strftime("%Y-%m-%d %H:%M"),
           (now + min10).strftime("%Y-%m-%d %H:%M")))
    output = open('metar.txt', 'w')
    output.write("\x01\r\r\n")
    output.write("000 \r\r\n")
    output.write("SAUS99 KISU %s\r\r\n" % (now.strftime("%d%H%M"),))
    output.write("METAR\r\r\n")
    for row in acursor:
        output.write(row[0]+"=\r\r\n")
    output.write("\x03\r\r\n")
    output.close()

def process_metar( now ):
    """
    Generate the GEMPAK file!
    """
    cmd = "cat metar.txt | dcmetr -c %s metar.gem" % (
                                        now.strftime("%Y%m%d/%H%M"),)
    subprocess.call(cmd, shell=True)

def generate_image( now ):
    """
    Generate the GEMPAK file!
    """
    cmd = "csh mwplot.csh %s" % (
                                        now.strftime("%Y %m %d %H %M"),)
    subprocess.call(cmd, shell=True)

sts = mx.DateTime.DateTime(1955,5,14,21)
ets = mx.DateTime.DateTime(1955,5,14,22)
interval = mx.DateTime.RelativeDateTime(hours=1)

now = sts
while now < ets:
    metar_extract( now )
    process_metar( now )
    generate_image( now )
    now += interval