"""
 11 Nov 2003	Augh, this never worked for the beginning!
"""

import access
import iemdb
import mx.DateTime
IEM = iemdb.connect('iem', bypass=True)
icursor = IEM.cursor()


def Main():
  ian = access.get_network("IA_RWIS", IEM)

  out = open("/tmp/rwis_surface.list", "w")
  out.write(""" PARM = TCS0;TCS1;TCS2;TCS3;SUBC

    STN    YYMMDD/HHMM      TCS0     TCS1     TCS2     TCS3     SUBC
""")

  thres = mx.DateTime.now() + mx.DateTime.RelativeDateTime(hours=-1)
  for id in ian.keys():
    if ian[id].data["valid"] > thres:
      m = ian[id].data["valid"].minute
      ian[id].data['ts'] = mx.DateTime.strptime(ian[id].data['valid'].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M")
      if (m > 45):
        ts = ian[id].data["ts"] + mx.DateTime.RelativeDateTime(hours=+1, minute=0)
      elif (m > 25):
        ts = ian[id].data["ts"] + mx.DateTime.RelativeDateTime(minute=40)
      elif (m >  5):
        ts = ian[id].data["ts"] + mx.DateTime.RelativeDateTime(minute=20)
      else:
        ts = ian[id].data["ts"] + mx.DateTime.RelativeDateTime(minute=0)
      out.write("%10s %16s %8s %8s %8s %8s %8s\n" % (
            id, ts.gmtime().strftime("%y%m%d/%H%M"), ian[id].data["tsf0"], 
           ian[id].data["tsf1"], ian[id].data["tsf2"], ian[id].data["tsf3"], 
           ian[id].data["rwis_subf"] ) )

  out.close()
Main()
