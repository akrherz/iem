# 11 Nov 2003	Augh, this never worked for the beginning!

from pyIEM import iemAccessNetwork, iemAccess
import mx.DateTime
iemaccess = iemAccess.iemAccess()

def Main():
  ian = iemAccessNetwork.iemAccessNetwork("IA_RWIS")
  #iemaccess.query("SET TIME ZONE 'GMT'")
  ian.getObs(iemaccess.iemdb)


  out = open("/tmp/rwis_surface.list", "w")
  out.write(""" PARM = TCS0;TCS1;TCS2;TCS3;SUBC

    STN    YYMMDD/HHMM      TCS0     TCS1     TCS2     TCS3     SUBC
""")

  thres = mx.DateTime.now() + mx.DateTime.RelativeDateTime(hours=-1)
  for id in ian.data.keys():
    if (ian.data[id]["ts"] > thres):
      m = ian.data[id]["ts"].minute
      if (m > 45):
        ts = ian.data[id]["ts"] + mx.DateTime.RelativeDateTime(hours=+1, minute=0)
      elif (m > 25):
        ts = ian.data[id]["ts"] + mx.DateTime.RelativeDateTime(minute=40)
      elif (m >  5):
        ts = ian.data[id]["ts"] + mx.DateTime.RelativeDateTime(minute=20)
      else:
        ts = ian.data[id]["ts"] + mx.DateTime.RelativeDateTime(minute=0)
      out.write("%10s %16s %8s %8s %8s %8s %8s\n" % \
        (id, ts.gmtime().strftime("%y%m%d/%H%M"), ian.data[id]["tsf0"], \
           ian.data[id]["tsf1"], ian.data[id]["tsf2"], ian.data[id]["tsf3"], \
           ian.data[id]["rwis_subf"] ) )

  out.close()
Main()
