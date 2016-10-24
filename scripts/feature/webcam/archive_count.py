import numpy as np
import matplotlib.pyplot as plt
# import psycopg2
# DBCONN = psycopg2.connect(database='mesosite', host='iemdb', user='nobody')
# cursor = DBCONN.cursor()

cnts = [188994, 1142944, 1425268, 2018777, 2626531, 3928237, 4994497,
        9774945, 12081458, 11880524, int(6637078.0 / 203.0 * 365.5)]
cnts = np.array(cnts) / 1000000.0
# for year in range(2003,2014):
#    cursor.execute("""SELECT count(*) from camera_log where
#    valid between '%s-01-01' and '%s-01-01'""" % (year, year+1))
#    row = cursor.fetchone()
#    cnts.append( row[0] )
#    print year, row[0]
#
# print cnts


(fig, ax) = plt.subplots(1, 1)

ax.imshow(plt.imread('KCCI-001_200307221435.jpg'),
          extent=(2003, 2007, 9.1, 14), aspect='auto')
ax.text(2005., 13.5, "Jefferson 22 Jul 2003", color='white', fontsize=14,
        ha='center')
ax.imshow(plt.imread('KCCI-001_201307221435.jpg'),
          extent=(2003, 2007, 4, 8.9), aspect='auto')
ax.text(2005., 8, "Jefferson 22 Jul 2013", color='white', fontsize=14,
        ha='center')
ax.bar(np.arange(2003, 2014) - 0.4, cnts, width=0.8)
ax.text(2003, 1, "KCCI-TV", ha='center', fontsize=10)
ax.text(2008, 4.1, "KELO-TV\nKCRG-TV", ha='center', fontsize=10)
ax.text(2010, 10, "Iowa DOT", ha='center', fontsize=10)
ax.set_xlim(2002.5, 2013.5)
ax.set_title("10 years of IEM Webcam Imagery")
ax.set_ylabel("Webcam Images Saved Per Year [millions]")
ax.set_xlabel("*2013 total extrapolated")


fig.savefig('test.png')
