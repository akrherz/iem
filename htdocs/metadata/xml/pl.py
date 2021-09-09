"""Generate the Starfish Fungis XML"""

from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable


def application(environ, start_response):
    """Do Something"""
    form = parse_formvars(environ)
    network = form.get("network", "ISUSM")
    nt = NetworkTable(network, only_online=False)
    station = form.get("station", "AEEI4")
    xs = """<?xml version="1.0" encoding="UTF-8"?>
<sfl:Platform
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:sfl="http://sawi.gst.com/nmpa/schema/sfl.xsd"
xmlns:gml="http://www.opengis.net/gml/3.2"
xmlns:swe="http://www.opengis.net/swe/2.0"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:gmd="http://www.isotc211.org/2005/gmd"
xmlns:nmpa="http://sawi.gst.com/nmpa/schema/metaExtension.xsd"
xsi:schemaLocation="http://sawi.gst.com/nmpa/schema/sfl.xsd"
gml:id="%(network)s_%(station)s">

<sfl:operator xlink:href="https://mesonet.agron.iastate.edu/metadata/xml/rp_IEM.xml"/>
<sfl:mobile>false</sfl:mobile>
<sfl:deployedAt>
  <sfl:PlatformDeployment gml:id="pd_%(network)s_%(station)s">
    <sfl:summary>
      This file describes the Iowa State Soil Moisture Network (ISUSM) station
      deployed at the %(name)s.
    </sfl:summary>

    <sfl:validTime>
      <gml:description>This block describes the date and time for when the platform was initially deployed during this instance.</gml:description>
      <gml:metaDataProperty></gml:metaDataProperty>
      <gml:name></gml:name>
      <swe:constraint></swe:constraint>
      <swe:quality></swe:quality>
      <swe:uom xlink:href="urn:x-ogc:def:uom:OGC:iso8601"/>
      <swe:value>%(sts)s</swe:value>
    </sfl:validTime>

    <sfl:deployer xlink:href="https://mesonet.agron.iastate.edu/metadata/xml/rp_IEM.xml"/>

    <sfl:deploymentLocation>
      <gml:Point srsName="urn:ogc:def:crs:EPSG::4326" srsDimension="3">
        <gml:pos>%(lat).4s %(lon).4s %(elev).1f</gml:pos>
      </gml:Point>
    </sfl:deploymentLocation>

    <sfl:siteCharacteristic>
      <nmpa:ExtendedMetadata>
        <nmpa:Reference xlink="http://sawi.gst.com/nmpa/MesoUS_Future_Metadata_04Apr2012.xlsx" />
        <nmpa:MetadataElement id="Platform_Distribution_Restrictions">
                <nmpa:value>4</nmpa:value>
        </nmpa:MetadataElement>
        <nmpa:MetadataElement id="Platform_Transmission_Method">
                <nmpa:value>"cellular"</nmpa:value>
        </nmpa:MetadataElement>
        <nmpa:MetadataElement id="Platform_Data_Format">
                <nmpa:value></nmpa:value>
        </nmpa:MetadataElement>
        <nmpa:MetadataElement id="Platform_Transmission_Frequency">
                <nmpa:value>"R/PT60M"</nmpa:value>
        </nmpa:MetadataElement>
        <nmpa:MetadataElement id="Platform_Slope_Value">
                <nmpa:value></nmpa:value>
        </nmpa:MetadataElement>
        <nmpa:MetadataElement id="Platform_Soil_Characteristics">
                <nmpa:value></nmpa:value>
        </nmpa:MetadataElement>
      </nmpa:ExtendedMetadata>
    </sfl:siteCharacteristic>

  </sfl:PlatformDeployment>

</sfl:deployedAt>
<sfl:deployedSensor xlink:href="https://mesonet.agron.iastate.edu/metadata/xml/sd_%(network)s_%(station)s.xml"/>
</sfl:Platform>""" % dict(
        network=network,
        station=station,
        name=nt.sts[station]["name"],
        lat=nt.sts[station]["lat"],
        elev=nt.sts[station]["elevation"],
        lon=nt.sts[station]["lon"],
        sts=nt.sts[station]["archive_begin"].strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    headers = [("Content-type", "text/xml")]
    start_response("200 OK", headers)
    return [xs.encode("ascii")]
