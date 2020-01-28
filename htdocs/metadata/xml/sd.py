"""Generate the Starfish Fungis XML"""

from paste.request import parse_formvars
from pyiem.network import Table as NetworkTable

IEM = "https://mesonet.agron.iastate.edu/metadata/xml"


def application(environ, start_response):
    """ Do Something"""
    form = parse_formvars(environ)
    network = form.get("network", "ISUSM")
    nt = NetworkTable(network, only_online=False)
    station = form.get("station", "AEEI4")
    xs = """<?xml version="1.0" encoding="UTF-8"?>
<sfl:SensorDeployment xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:sfl="http://sawi.gst.com/nmpa/schema/sfl.xsd"
xmlns:gml="http://www.opengis.net/gml/3.2"
xmlns:swe="http://www.opengis.net/swe/2.0"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://sawi.gst.com/nmpa/schema/sfl.xsd"
gml:id="sd_%(network)s_%(station)s">

  <sfl:validTime>
    <swe:TimeRange>
      <swe:uom code="ISO8601"/>
      <swe:value>%(sts)s 9999-12-31T23:59</swe:value>
    </swe:TimeRange>
  </sfl:validTime>
  <sfl:deployer xlink:href="%(iem)s/rp_IEM.xml"/>
  <sfl:deploymentLocation>
    <gml:Point srsName="urn:ogc:def:derivedCRSType:OGC:1.0:engineering">
      <gml:pos dimension="3" uomLabels="m m m"> 0 0 13.1</gml:pos>
    </gml:Point>
  </sfl:deploymentLocation>

  <sfl:mobile>false</sfl:mobile>

  <sfl:deploys>

    <!-- Wind -->
    <sfl:Sensor gml:id="CS_03002">
      <sfl:serialNumber></sfl:serialNumber>
      <sfl:characteristics xlink:href="%(iem)s/sc_CS_03002.xml"/>
      <sfl:senses>
        <sfl:Sensing gml:id="CS_03002_1">
    <sfl:sensingProcedure xlink:href="%(iem)s/sp_CS_03002_WindSpeed.xml" />
          <sfl:unitOfMeasure uom="m/s"/>
          <sfl:active>true</sfl:active>
        </sfl:Sensing>
        <sfl:Sensing gml:id="CS_03002_2">
    <sfl:sensingProcedure xlink:href="%(iem)s/sp_CS_03002_WindDirection.xml" />
          <sfl:unitOfMeasure uom="deg"/>
          <sfl:active>true</sfl:active>
        </sfl:Sensing>
      </sfl:senses>
    </sfl:Sensor>

    <!-- Temp + RH -->
    <sfl:Sensor gml:id="CS_CS215">
      <sfl:serialNumber></sfl:serialNumber>
      <sfl:characteristics xlink:href="%(iem)s/sc_CS_CS215.xml"/>
      <sfl:senses>
        <sfl:Sensing gml:id="CS_CS215_1">
          <sfl:sensingProcedure xlink:href="%(iem)s/sp_CS_CS215_Temp.xml" />
          <sfl:unitOfMeasure uom="C"/>
          <sfl:active>true</sfl:active>
        </sfl:Sensing>
        <sfl:Sensing gml:id="CS_CS215_2">
          <sfl:sensingProcedure xlink:href="%(iem)s/sp_CS_CS215_RH.xml" />
          <sfl:unitOfMeasure uom="%%"/>
          <sfl:active>true</sfl:active>
        </sfl:Sensing>
      </sfl:senses>
    </sfl:Sensor>

    <!-- Solar Rad-->
    <sfl:Sensor gml:id="CS_CS300">
      <sfl:serialNumber></sfl:serialNumber>
      <sfl:characteristics xlink:href="%(iem)s/sc_CS_CS300.xml"/>
      <sfl:senses>
        <sfl:Sensing gml:id="CS_CS300_1">
          <sfl:sensingProcedure xlink:href="%(iem)s/sp_CS_CS300.xml" />
          <sfl:unitOfMeasure uom="J m-2 s-1"/>
          <sfl:active>true</sfl:active>
        </sfl:Sensing>
      </sfl:senses>
    </sfl:Sensor>

    <!-- Soil Moisture and Temp -->
    <sfl:Sensor gml:id="CS_CS655">
      <sfl:serialNumber></sfl:serialNumber>
      <sfl:characteristics xlink:href="%(iem)s/sc_CS_CS655.xml"/>
      <sfl:senses>
        <sfl:Sensing gml:id="CS_CS655_1">
    <sfl:sensingProcedure xlink:href="%(iem)s/sp_CS_CS655_Temp.xml" />
          <sfl:unitOfMeasure uom="K"/>
          <sfl:active>true</sfl:active>
        </sfl:Sensing>
        <sfl:Sensing gml:id="CS_CS655_2">
    <sfl:sensingProcedure xlink:href="%(iem)s/sp_CS_CS655_Moisture.xml" />
          <sfl:unitOfMeasure uom="kg kg-1"/>
          <sfl:active>true</sfl:active>
        </sfl:Sensing>
      </sfl:senses>
    </sfl:Sensor>

    <!-- Precip -->
    <sfl:Sensor gml:id="CS_TE525">
      <sfl:serialNumber></sfl:serialNumber>
      <sfl:characteristics xlink:href="%(iem)s/sc_CS_TE525.xml"/>
      <sfl:senses>
        <sfl:Sensing gml:id="CS_TE525_1">
          <sfl:sensingProcedure xlink:href="%(iem)s/sp_CS_TE525.xml" />
          <sfl:unitOfMeasure uom="mm"/>
          <sfl:active>true</sfl:active>
        </sfl:Sensing>
      </sfl:senses>
    </sfl:Sensor>

  </sfl:deploys>

  <sfl:boundTo xlink:href="%(iem)s/pl_%(network)s_%(station)s.xml" />

</sfl:SensorDeployment>
""" % dict(
        network=network,
        station=station,
        name=nt.sts[station]["name"],
        lat=nt.sts[station]["lat"],
        iem=IEM,
        lon=nt.sts[station]["lon"],
        sts=nt.sts[station]["archive_begin"].strftime("%Y-%m-%dT%H:%M:%SZ"),
    )

    headers = [("Content-type", "text/xml")]
    start_response("200 OK", headers)
    return [xs.encode("ascii")]
