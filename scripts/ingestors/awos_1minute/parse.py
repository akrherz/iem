#!/mesonet/python/bin/python
# 10 Oct 2002:	Remove Time Contraint
# 11 Jul 2003	Use Site python, connect to a DB that works

from pyIEM import awosOb
import sys, mx.DateTime

ts = mx.DateTime.DateTime(int(sys.argv[1]), int(sys.argv[2]), 1)

stations = ["AXA","IKV","AIO","ADU","BNW","CIN","CNC","CCY","ICL","CAV",
 "CWI","CBF","CSQ","DEH","DNS","FFL","FOD","FSW","HNR","EOK","OXV","LRJ",
  "MXO","MUT","TNU","OLZ","ORC","RDK","SHL","SDA","SLB","AWG","EBS",
  "PEA","MPZ","VTI","IIB","CKP","OOA","GGI","TVK","IFA","PRO","FXY","I75"]


for station in stations:
  i = open("station/"+station+".dat").readlines()

  out = open('DB/'+station+'.db', 'w')
  out.write("SET TIME ZONE 'GMT';\n")
  out.write("COPY t%s FROM stdin WITH NULL as 'Null';\n" % (
            ts.strftime("%Y_%m"),))
  ba = mx.DateTime.DateTime(1900,1,1)
  for line in i:
    try:
      myOb = awosOb.awosOb(line)
    except:
      print line
    myOb.writeDBF(out)
  out.write("\.\n")
  out.close()
