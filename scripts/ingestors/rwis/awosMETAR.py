"""
 Process AWOS METAR file 
"""
import re
import tempfile
import os
import mx.DateTime
import subprocess
gmt = mx.DateTime.gmt()

data = {}
for line in open('/mesonet/data/incoming/iaawos_metar.txt', 'r'):
    m = re.match("METAR K(?P<id>[A-Z1-9]{3})", line)
    if not m:
      continue
    d = m.groupdict()
    data[ d['id'] ] = line
    
fd, path = tempfile.mkstemp()
#os.write(fd,  '000\r\nNZUS99 KDMX %s\r\n' % (gmt.strftime("%d%H%M"),)) 
for id in data.keys():
    os.write(fd, '%s=\r\n' % (data[id].strip().replace("METAR ", ""),))
os.close(fd)
p = subprocess.Popen("/home/ldm/bin/pqinsert -p 'data c 000000000000 LOCDSMMETAR.dat LOCDSMMETAR.dat txt' %s" % (path,),
                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
os.waitpid(p.pid, 0)
os.remove(path) 
