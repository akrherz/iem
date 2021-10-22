EAST = ["fulldisk", "conus", "mesoscale-1", "mesoscale-2", "puertorico"]
WEST = ["fulldisk", "conus", "mesoscale-1", "mesoscale-2", "alaska", "hawaii"]
for sector in WEST:
    for channel in range(1, 17):
        print(
            """
LAYER
  NAME "%(sector)s_ch%(channel)02i"
  STATUS ON
  DATA "/mesonet/ldmdata/gis/images/GOES/%(sector)s/channel%(channel)02i/GOES-16_C%(channel)02i.png"
  TYPE RASTER
  MINSCALE 0
  MAXSCALE 465000000
  INCLUDE "/mesonet/ldmdata/gis/images/GOES/%(sector)s/channel%(channel)02i/GOES-16_C%(channel)02i.msinc"
  PROCESSING "CLOSE_CONNECTION=NORMAL"
END"""
            % dict(sector=sector, channel=channel)
        )
