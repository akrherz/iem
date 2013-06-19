"""
Deployment for /etc/hosts
"""

import os
import re
import subprocess
import shutil
import datetime

fn = os.path.join( os.path.dirname(__file__) , '../config/etc-hosts.txt')
second_network = False
proc = subprocess.Popen('/sbin/ifconfig', stdout=subprocess.PIPE)
for line in proc.stdout:
    if re.match("^inet addr:192\.168\.1\.", line.strip()):
        second_network = True
        

data = open(fn).read()
replace = "0"
if second_network:
    replace = "1"
    
data = data.replace("$net$", replace)

shutil.copyfile('/etc/hosts', '/tmp/etc_hosts.%s' % (
                    datetime.datetime.now().strftime("%Y%m%d%H%M"),) )
o = open("/etc/hosts", 'w')
o.write(data)
o.close()