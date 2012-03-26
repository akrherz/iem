import iemdb
import network
import mx.DateTime
iem = iemdb.connect('iem', bypass=True)
icursor = iem.cursor()

nt = network.Table(["IA_ASOS","AWOS"])

maxV = [0]*500

for id in nt.sts.keys():
  icursor.execute("""SELECT valid, tmpf from current_log c JOIN stations s
  on (c.iemid = s.iemid) WHERE s.id = '%s' and s.network in ('IA_ASOS','AWOS')
  and valid > 'TODAY' and tmpf > 0 ORDER by valid ASC""" % (id,))
  valid = []
  tmpf = []
  for row in icursor:
    valid.append( mx.DateTime.strptime(row[0].strftime("%Y%m%d%H%M"), "%Y%m%d%H%M") )
    tmpf.append( row[1] )

  for i in range(10,len(valid)):
    for k in range(1,10):
      deltaT = (valid[i] - valid[i-k]).minutes
      diffTemp = (tmpf[i] - tmpf[i-k])
      if diffTemp < maxV[int(deltaT/10)]:
        print deltaT, diffTemp, id, valid[i]
        maxV[int(deltaT/10)] = diffTemp
