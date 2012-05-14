"""
I do silly things, then need to do more silly things to correct
"""
import glob
import mx.DateTime
import os

def doit():
  targets = glob.glob("GOES_[(EAST)|(WEST)]*")
  if len(targets) == 0:
    return
  if not os.path.isdir("awips211"):
    os.mkdir("awips211")
  for target in targets:
    os.rename(target, "awips211/%s" % (target,))

"""
def doit():
  targets = glob.glob("awips*") + glob.glob("GOES[1-9]*")
  for target in targets:
    if os.path.isfile(target):
      newname = "GOES_%s" % ("_".join(target.split("_")[1:]),)
      print target, newname
      os.rename(target,newname)
    else:
      os.chdir(target)
      doit()
      os.chdir("..")
"""

sts = mx.DateTime.DateTime(2012,3,22)
ets = mx.DateTime.DateTime(2011,3,22)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts

while now > ets:
  print now
  os.chdir( now.strftime("/mesonet/ARCHIVE/data/%Y/%m/%d/GIS/sat") )
  doit()
  now -= interval
