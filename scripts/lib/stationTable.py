# Python class for handling station tables
# Daryl Herzmann 20 Feb 2002
#  1 May 2002:    Support for different kinds of work
#  5 Jun 2002:    Include GIS in station Table
#  4 Dec 2002:    Lets add some generic support for building
#        and writing station tables?
# 17 May 2003    Bump the lon value over one more place to get the correct vals
# 20 Aug 2003    Must format station name in correct places
#####################################################

import string

class stationTable:
  def __init__(self, tableName, loadTable = "yes"):
    self.ids = []
    self.names = {}
    self.sts = {}
    self.tableName = tableName
    if (loadTable == "yes"):
      self.load()

  def empty(self):
    self.ids = []
    self.names = {}
    self.sts = {}

  def editRow_mesosite(self, rs):
    thisID = rs["id"]
    st = {}
    st["id"] = thisID
    self.ids.append(thisID)
    st["synop"] = rs["synop"]
    st["name"] = rs["plot_name"]
    st["state"] = rs["state"]
    st["country"] = rs["country"]
    st["lat"] = rs["latitude"]
    st["lon"] = rs["longitude"]
    st["gis"] = "POINT("+ str(st["lon"]) +" "+ str(st["lat"]) +")"
    st["elev"] = rs["elevation"]
    if (rs["spri"] == None):
      st["spri"] = " "
    else:
      st["spri"] = rs["spri"]
    self.sts[thisID] = st

  def writeTable(self, o):
    import string
    for sid in self.ids:
       st = self.sts[sid]
       o.write("%-8s %6s %-32.32s %2s %2s %5.0f %6.0f %4.0f %2s\n" % \
        (st["id"], st["synop"], st["name"], \
         st["state"], st["country"], st["lat"] * 100 , st["lon"] * 100, \
         int(st["elev"]), st["spri"]) )

  def load(self):
    f = open(self.tableName, 'r').readlines()
    for line in f:
      if (line[0] != "#"):
        thisID = string.strip( line[0:8] )
        synop  = string.strip( line[9:15] )
        sname  = string.strip( line[16:48] )
        state  = string.strip( line[49:51] )
        country  = string.strip( line[52:54] )
        lat  = string.strip( line[55:60] )
        lon  = string.strip( line[61:68] )
        elev = string.strip( line[68:73] )
        spri = string.strip( line[74:76] )

        if (len(elev) == 0): elev = "343"
            
        # Time to update 
        self.ids.append(thisID)
        self.names[thisID] = sname
        st = {}
        st["id"] = thisID
        st["synop"] = synop
        st["name"] = sname
        st["state"] = state
        st["country"] = country
        st["lat"] = round( int(lat) / 100.00, 2)
        st["lon"] = round( int(lon) / 100.00, 2)
        st["gis"] = "POINT("+ str(st["lon"]) +" "+ str(st["lat"]) +")"
        st["elev"] = elev
        st["spri"] = spri            
        self.sts[thisID] = st

#       print thisID, synop, sname, state, country, lat, lon, elev, spri
#       print self.names
