#
# Logic to completely remove an ASOS site from our archives
# The site may have never been online or IEM has no data archive of it
import iemdb
MESOSITE = iemdb.connect('mesosite')
mcursor = MESOSITE.cursor()
IEM = iemdb.connect('iem')
icursor = IEM.cursor()

import sys
id = sys.argv[1]
network = sys.argv[2]

# Remove from IEM
icursor.execute("""
DELETE from current where station = %s and network = %s
""", (id, network))
icursor.execute("""
DELETE from summary where station = %s and network = %s
""", (id, network))
icursor.execute("""
DELETE from trend_1h where station = %s and network = %s
""", (id, network))
icursor.execute("""
DELETE from trend_15m where station = %s and network = %s
""", (id, network))

mcursor.execute("""
DELETE from stations where id = %s and network = %s
""", (id, network))

mcursor.close()
icursor.close()
IEM.commit()
MESOSITE.commit()
