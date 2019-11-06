""" Verify that a RASTER's colortable matches documentation
"""

import numpy as np
from pandas.io.sql import read_sql
import requests
from PIL import Image
from pyiem.util import get_dbconn, logger

LOG = logger()


def main():
    """Do something"""
    # Get the listing
    pgconn = get_dbconn("mesosite")
    cursor = pgconn.cursor()
    cursor.execute(
        """
        SELECT id from iemrasters where name = 'composite_n0q'
    """
    )
    rasterid = cursor.fetchone()[0]
    df = read_sql(
        """
        SELECT * from iemrasters_lookup WHERE iemraster_id = %s
        ORDER by coloridx ASC
        """,
        pgconn,
        params=(rasterid,),
        index_col="coloridx",
    )
    # Go get a raster
    req = requests.get(
        (
            "https://mesonet.agron.iastate.edu/archive/data/"
            "2012/09/01/GIS/uscomp/n0q_201209010000.png"
        )
    )
    fh = open("/tmp/check_raster.png", "wb")
    fh.write(req.content)
    fh.close()
    # Read the color table
    img = Image.open("/tmp/check_raster.png")
    flat = np.array(img.getpalette())
    # pylint: disable=unsubscriptable-object
    palette = np.reshape(flat, (int(flat.shape[0] / 3), 3))
    for coloridx, rgb in enumerate(palette):
        row = df.loc[coloridx]
        if rgb[0] != row["r"] or rgb[1] != row["g"] or rgb[2] != row["b"]:
            LOG.info(
                "Mismatch coloridx:%s PNG: %s,%s,%s Docs: %s,%s,%s",
                coloridx,
                rgb[0],
                rgb[1],
                rgb[2],
                row["r"],
                row["g"],
                row["b"],
            )


if __name__ == "__main__":
    main()
