import urllib2
import json

URI = ("https://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/"
       "Road_Conditions/MapServer/1/query?text=&geometry=&"
       "geometryType=esriGeometryPoint&inSR="
       "&spatialRel=esriSpatialRelIntersects&relationParam=&objectIds="
       "&where=label+is+not+null&time=&returnCountOnly=false&"
       "returnIdsOnly=false&returnGeometry=true&maxAllowableOffset="
       "&outSR=&outFields=*&f=json")

j = json.loads(urllib2.urlopen(URI).read())
print j
# http://services.arcgis.com/8lRhdTsQyJpO52F1/ArcGIS/rest/services/Road_Conditions/FeatureServer
