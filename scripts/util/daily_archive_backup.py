"""Send a tar file of our daily data to CyBox!

Note, needs a ~/.netrc file with 600 perms

Lets run at 12z for the previous date
"""
import datetime
import subprocess
import os
import sys
import glob


def run(date):
    """Upload this date's worth of data!"""
    os.chdir("/mesonet/tmp")
    tarfn = date.strftime("iem_%Y%m%d.tgz")
    # Step 1: Create a gzipped tar file
    cmd = "tar -czf %s /mesonet/ARCHIVE/data/%s" % (tarfn,
                                                    date.strftime("%Y/%m/%d"))
    subprocess.call(cmd, shell=True, stderr=subprocess.PIPE)
    sz = os.path.getsize(tarfn)
    if sz > 14000000000:
        # Step 2: Split this big file into 14GB chunks, each file will have
        # suffix .aa then .ab then .ac etc
        cmd = "split --bytes=14000M %s %s." % (tarfn, tarfn,)
        subprocess.call(cmd, shell=True, stderr=subprocess.PIPE)
        files = "; ".join(["put %s" % (x, )
                           for x in glob.glob("%s.??" % (tarfn, ))])
    else:
        files = "put %s" % (tarfn, )
    # Step 3: Create a series of put commands to send each of these split files
    # up to box
    cmd = ("lftp -u akrherz@iastate.edu -e 'cd IEMArchive; mkdir %s; cd %s; "
           " %s; bye' "
           "ftps://ftp.box.com") % (date.year, date.year, files)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    print("CyBox: %s\n%s" % (tarfn, proc.stdout.read()))
    # Step 5: delete uploaded files!
    for fn in glob.glob("%s*" % (tarfn,)):
        os.unlink(fn)


def main(argv):
    if len(argv) == 2:
        now = datetime.date(int(argv[1]), 1, 1)
        ets = datetime.date(int(argv[1]) + 1, 1, 1)
        while now < ets:
            run(now)
            now += datetime.timedelta(days=1)
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        run(yesterday)

if __name__ == '__main__':
    main(sys.argv)
