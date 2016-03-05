"""
script to send the MZZU data to LDM

daryl herzmann akrherz@iastate.edu
"""
import subprocess
import sys
import glob
import os

DIRNAME = "/data/ewrtemp/"
PQINSERT = "/home/ldm/bin/pqinsert"
LDMQUEUE = "/home/ldm/var/queues/ldm.pq"


def send2ldm(fn):
    """Send this file to LDM"""
    #  L2-BZIP2/KAMA/20160305012732/282/6/I/V06/0
    # MZZU_20160304_2352_1_I
    tokens = fn.split("_")
    if len(tokens) != 5:
        print("Invalid filename for send2ldm: '%s'" % (fn, ))
        return
    product_name = ("L2-BZIP2/%s/%s%s00/000/%s/%s/V06/0"
                    ) % (tokens[0], tokens[1], tokens[2], tokens[3],
                         tokens[4])
    cmd = ("%s -p '%s' -f NEXRAD2 -i -v -q %s %s"
           ) % (PQINSERT, product_name, LDMQUEUE, fn)
    subprocess.call(cmd, shell=True)

def main(argv):
    """ code entry """
    os.chdir(DIRNAME)
    # Get all files with name starting with MZZU
    files = glob.glob("MZZU*")
    # Sort them by their creation time
    files.sort(key=lambda x: os.path.getctime(x))
    map(send2ldm, files)

if __name__ == '__main__':
    main(sys.argv)
