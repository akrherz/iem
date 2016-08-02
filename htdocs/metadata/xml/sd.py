#!/usr/bin/env python
"""Generate the Starfish Fungis XML"""
import cgi
import sys
from pyiem.network import Table as NetworkTable


def main():
    """ Do Something"""
    form = cgi.FieldStorage()
    network = form.getfirst('network', 'ISUSM')
    nt = NetworkTable(network)
    station = form.getfirst('station', 'AEEI4')
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
  <sfl:deployer xlink:href="https://mesonet.agron.iastate.edu/metadata/xml/rp_IEM.xml"/>
  <sfl:deploymentLocation>
    <gml:Point srsName="urn:ogc:def:derivedCRSType:OGC:1.0:engineering">
      <gml:pos dimension="3" uomLabels="m m m"> 0 0 13.1</gml:pos>
    </gml:Point>
  </sfl:deploymentLocation>

  <sfl:mobile>false</sfl:mobile>

  <sfl:deploys>

    <sfl:Sensor gml:id="CS_03002">
      <sfl:serialNumber></sfl:serialNumber>
      <sfl:characteristics xlink:href="https://mesonet.agron.iastate.edu/metadata/xml/sc_CS_03002.xml"/>
      <sfl:senses>
        <sfl:Sensing gml:id="CS_03002_1">
          <sfl:sensingProcedure xlink:href="https://mesonet.agron.iastate.edu/metadata/xml/sp_CS_03002.xml" />
          <sfl:unitOfMeasure uom="m/s"/>
          <sfl:active>true</sfl:active>
        </sfl:Sensing>
      </sfl:senses>
    </sfl:Sensor>

  </sfl:deploys>

  <sfl:boundTo xlink:href="https://mesonet.agron.iastate.edu/metadata/xml/pl_%(network)s_%(station)s.xml" />

</sfl:SensorDeployment>
""" % dict(network=network, station=station,
           name=nt.sts[station]['name'],
           lat=nt.sts[station]['lat'],
           lon=nt.sts[station]['lon'],
           sts=nt.sts[station]['archive_begin'].strftime("%Y-%m-%dT%H:%M:%SZ"))

    sys.stdout.write("Content-type: text/xml\n\n")
    sys.stdout.write(xs)

if __name__ == '__main__':
    main()
