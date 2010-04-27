# Need something to check the 5 day KCCI image
# Daryl Herzmann 3 Mar 2004

import stat, os, time

file = "/mesonet/share/pickup/kcci/extended.jpg"

mtime = os.stat(file)[stat.ST_MTIME]

now = time.time()

if ( (now - mtime) > 86400):
  os.system('echo "OLD 5DAY" | mail -s "KCCI 5DAY OFF" akrherz@iastate.edu')

