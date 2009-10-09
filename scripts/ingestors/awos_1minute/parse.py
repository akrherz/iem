#!/mesonet/python/bin/python
# 10 Oct 2002:	Remove Time Contraint
# 11 Jul 2003	Use Site python, connect to a DB that works

from pyIEM import awosOb
import sys, mx.DateTime

year = str(sys.argv[1])
month = str(sys.argv[2])

stations = ["AXA","IKV","AIO","ADU","BNW","CIN","CNC","CCY","ICL","CAV",
 "CWI","CBF","CSQ","DEH","DNS","FFL","FOD","FSW","HNR","EOK","OXV","LRJ",
  "MXO","MUT","TNU","OLZ","ORC","RDK","SHL","SDA","SLB","AWG","EBS",
  "PEA","MPZ","VTI","IIB","CKP","OOA","GGI","TVK","IFA","PRO","FXY","I75"]


for station in stations:
  i = open("station/"+station+".dat").readlines()

# COPY t2001_01 FROM stdin;
#DATA TDF
#\.
  out = open('DB/'+station+'.db', 'w')
  out.write("SET TIME ZONE 'GMT';\n")
#  out.write("""
#create table t1999_06 (station varchar(5), valid timestamp, tmpf int2, 
#dwpf int2, sknt int2, drct int2, gust int2, p01i real, cl1 int2, ca1 int2,
#cl2 int2, ca2 int2, cl3 int2, ca3 int2, vsby real, alti real, qc varchar(5) );
#create index t1999_06_valid_idx on t1999_06(valid);
#create index t1999_06_stn_idx on t1999_06(station);
#grant select on t1999_06 to nobody;
#""")
  out.write("COPY t"+ year +"_"+ month +" FROM stdin WITH NULL as 'Null';\n")
  ba = mx.DateTime.DateTime(1900,1,1)
  for line in i:
    try:
      myOb = awosOb.awosOb(line)
    except:
      print line
#    if myOb.gmt_ts > ba :
    myOb.writeDBF(out)
#      ba = myOb.gmt_ts

  out.write("\.\n")
  out.close()

###
#create table t2001_01 (station varchar(5), valid timestamp, tmpf real, 
#dwpf real, sknt real, drct real, gust real, p01i real, cl1 real, ca1 real, 
#cl2 real, ca2 real, cl3 real, ca3 real, vsby real, alti real, qc varchar(5) );

#create index t2001_01_idx on t2001_01(station, valid);
#create index t2001_01_stn_idx on t2001_01(station);

###
