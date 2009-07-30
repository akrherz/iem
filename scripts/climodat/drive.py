# Need something to drive the yearly plots, since Ngl no happy

import os

for i in range(1893,2009):
  for app in ['yearly_precip.py', 'avg_temp.py']:
    os.system("python %s %s" % (app, i))
