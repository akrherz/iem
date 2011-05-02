# Process AWOS METAR file 

import re, tempfile, os, mx.DateTime
gmt = mx.DateTime.gmt()

data = {}
for line in open('/mesonet/data/incoming/iaawos_metar.txt', 'r'):
    m = re.match("METAR K(?P<id>[A-Z]{3})", line)
    if not m:
      continue
    d = m.groupdict()
    data[ d['id'] ] = line
    
fd, path = tempfile.mkstemp()
os.write(fd,  '000\r\nNZUS99 KDMX %s\r\n' % (gmt.strftime("%d%H%M"),)) 
for id in data.keys():
    os.write(fd, '%s=\r\n' % (data[id].strip(),))
os.close(fd)
os.system("/home/ldm/bin/pqinsert -p 'LOCDSMMETAR.dat' %s" % (path,)) 
os.remove(path) 
