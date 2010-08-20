
import os
import shutil
import mx.DateTime

storePath = '/mnt/mesonet/data/agclimate/'
incomingPath = '/mnt/home/agclimo/incoming/campbell/'

now = mx.DateTime.now()
todayFile = now.strftime("D%d%b%y.TXT")

if os.path.isfile("%s/%s" % (incomingPath, todayFile)):
  dataFile = incomingPath+todayFile
  resultFile = storePath+todayFile

  shutil.copy2(dataFile, resultFile)
  os.remove(dataFile)

  os.system('sh run_plots.sh')
