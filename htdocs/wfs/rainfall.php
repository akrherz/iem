<?php
  header("Content-type: application/vnd.ogc.gml");
 ?>
<!DOCTYPE WMT_MS_Capabilities SYSTEM "http://www.digitalearth.gov/wmt/xml/capabilities_1_1_1.dtd"
 [
 <!ELEMENT VendorSpecificCapabilities EMPTY>
 ]>  <!-- end of DOCTYPE declaration -->

<WMT_MS_Capabilities version="1.1.1" updateSequence="0">
<Service> <!-- a service IS a MapServer mapfile -->
  <Name>GetMap</Name> <!-- WMT defined -->
  <Title>IEM WMS Service</Title>
  <Abstract>Ba Ba Ba</Abstract>
  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.wms?map=/mesonet/www/html/GIS/apps/wfs/wfs.map&amp;"/>
  <ContactInformation>
    <ContactPersonPrimary>
      <ContactPerson>Daryl Herzmann</ContactPerson>
      <ContactOrganization>Iowa State University</ContactOrganization>
    </ContactPersonPrimary>
  </ContactInformation>
  <AccessConstraints>None</AccessConstraints>
</Service>
<Capability>
  <Request>
    <GetCapabilities>
      <Format>application/vnd.ogc.wms_xml</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.wms?map=/mesonet/www/html/GIS/apps/wfs/wfs.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.wms?map=/mesonet/www/html/GIS/apps/wfs/wfs.map&amp;"/></Post>
        </HTTP>
      </DCPType>
    </GetCapabilities>
    <GetMap>
      <Format>image/png</Format>
      <Format>image/jpeg</Format>
      <Format>image/wbmp</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.wms?map=/mesonet/www/html/GIS/apps/wfs/wfs.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.wms?map=/mesonet/www/html/GIS/apps/wfs/wfs.map&amp;"/></Post>
        </HTTP>
      </DCPType>
    </GetMap>
    <GetFeatureInfo>
      <Format>text/plain</Format>
      <Format>text/html</Format>
      <Format>application/vnd.ogc.gml</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.wms?map=/mesonet/www/html/GIS/apps/wfs/wfs.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.wms?map=/mesonet/www/html/GIS/apps/wfs/wfs.map&amp;"/></Post>
        </HTTP>
      </DCPType>
    </GetFeatureInfo>
  </Request>
  <Exception>
    <Format>application/vnd.ogc.se_xml</Format>
    <Format>application/vnd.ogc.se_inimage</Format>
    <Format>application/vnd.ogc.se_blank</Format>
  </Exception>
  <VendorSpecificCapabilities />
  <Layer>
    <Name>iemtest</Name>
    <Title>IEM WMS Service</Title>
    <SRS>EPSG:26915</SRS>
    <LatLonBoundingBox minx="-96.7539" miny="39.6972" maxx="-90.3709" maxy="44.2532" />
    <BoundingBox SRS="EPSG:26915"
                minx="200000" miny="4.4e+06" maxx="710000" maxy="4.9e+06" />
    <ScaleHint min="44.9013" max="2319.9" />
    <Layer queryable="0" opaque="0" cascaded="0">
        <Name>counties</Name>
        <Title>Iowa Counties</Title>
        <SRS>EPSG:26915</SRS>
        <LatLonBoundingBox minx="-96.6849" miny="40.3328" maxx="-90.0694" maxy="43.557" />
        <BoundingBox SRS="EPSG:26915"
                    minx="202074" miny="4.4706e+06" maxx="736849" maxy="4.82267e+06" />
    </Layer>
  </Layer>
</Capability>
</WMT_MS_Capabilities>
