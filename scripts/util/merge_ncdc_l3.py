"""
 For some reason, I did not archive NCR for IEM archives,
 lets take NCDC's files and then merge NCR into my archived data!
"""
import datetime
import os
import subprocess
import glob
import shutil
# 1. Loop over days
now = datetime.datetime(2009, 1, 1)
ets = datetime.datetime(2011, 1, 1)
interval = datetime.timedelta(days=1)
while now < ets:
    # 2. Loop over nexrads
    for nexrad in ["FSD", "DMX", "DVN", "ARX", "OAX", "MPX"]:
        print '+ run %s %s' % (now, nexrad)
        os.chdir("/tmp/l3")
        os.makedirs("old")
        os.makedirs("new")

        oldfn = now.strftime(("/mesonet/ARCHIVE/nexrad/%Y_%m/" + nexrad +
                              "_%Y%m%d.tgz"))
        newfn = now.strftime(("/mesonet/tmp/level3/K" + nexrad +
                              "%Y%m%d.tar.Z"))
        # 3. Extract IEM archive into /tmp/l3/old
        os.chdir("/tmp/l3/old")
        if os.path.isfile(oldfn):
            subprocess.call("tar -xzf %s" % (oldfn,), shell=True)
        else:
            print "%s missing" % (oldfn,)
        if not os.path.isdir("NCR"):
            os.makedirs("NCR")
        # 4. Extract NCDC archive into /tmp/l3/new
        os.chdir("/tmp/l3/new")
        if os.path.isfile(newfn):
            subprocess.call("tar -xzf %s" % (newfn,), shell=True)
        else:
            print "%s missing" % (newfn,)
        # 5. Find NCR files in new/ and properly rename them into old/
        for oldncr in glob.glob("*_NCR???_*"):
            # old KFSD_SDUS83_DPAFSD_200901012223
            # new N3R/N3R_20090101_2059
            newncr = "/tmp/l3/old/NCR/NCR_%s_%s" % (oldncr[-12:-4],
                                                    oldncr[-4:])
            shutil.copyfile(oldncr, newncr)
        # 6. Regenerate the tar file
        os.chdir("/tmp/l3/old")
        subprocess.call("tar -czf %s ???" % (oldfn,), shell=True)
        # 7. Cleanup the new and old folders
        os.chdir("/tmp/l3")
        subprocess.call("rm -rf old new", shell=True)

    now += interval
