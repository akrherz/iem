""" Verify that a RASTER's colortable matches documentation
"""
import sys
import numpy as np
import psycopg2
from pandas.io.sql import read_sql
import requests
from PIL import Image
PGCONN = psycopg2.connect(database="mesosite", host='iemdb', user='nobody')


def main(argv):
    """Do something"""
    # Get the listing
    cursor = PGCONN.cursor()
    cursor.execute("""
        SELECT id from iemrasters where name = 'composite_n0q'
    """)
    rasterid = cursor.fetchone()[0]
    df = read_sql("""
        SELECT * from iemrasters_lookup WHERE iemraster_id = %s
        ORDER by coloridx ASC
        """, PGCONN, params=(rasterid,), index_col='coloridx')
    # Go get a raster
    req = requests.get(("http://mesonet.agron.iastate.edu/archive/data/"
                        "2012/09/01/GIS/uscomp/n0q_201209010000.png"))
    o = open('/tmp/check_raster.png', 'wb')
    o.write(req.content)
    o.close()
    # Read the color table
    img = Image.open('/tmp/check_raster.png')
    flat = np.array(img.getpalette())
    palette = np.reshape(flat, (flat.shape[0] / 3, 3))
    for coloridx, rgb in enumerate(palette):
        row = df.loc[coloridx]
        if rgb[0] != row['r'] or rgb[1] != row['g'] or rgb[2] != row['b']:
            print(("Mismatch coloridx:%s PNG: %s,%s,%s Docs: %s,%s,%s"
                   ) % (coloridx, rgb[0], rgb[1], rgb[2],
                        row['r'], row['g'], row['b']))

if __name__ == '__main__':
    main(sys.argv)
