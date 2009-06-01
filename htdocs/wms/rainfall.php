<?php
  header("Content-type: application/vnd.ogc.gml");
 ?>
<!DOCTYPE WMT_MS_Capabilities SYSTEM "http://www.digitalearth.gov/wmt/xml/capabilities_1_1_1.dtd"
 [
 <!ELEMENT VendorSpecificCapabilities EMPTY>
 ]>  <!-- end of DOCTYPE declaration -->

<WMT_MS_Capabilities version="1.1.1" updateSequence="0">
<Service> 
  <Name>GetMap</Name> <!-- WMT defined -->
  <Title>IEM Rainfall WFS Service</Title>
  <Abstract>IEM WFS Rainfall Service</Abstract>
  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv?map=/var/www/htdocs/GIS/apps/rainfall/wms.map&amp;"/>
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
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv?map=/var/www/htdocs/GIS/apps/rainfall/wms.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv?map=/var/www/htdocs/GIS/apps/rainfall/wms.map&amp;"/></Post>
        </HTTP>
      </DCPType>
    </GetCapabilities>
    <GetMap>
      <Format>image/png</Format>
      <Format>image/jpeg</Format>
      <Format>image/wbmp</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv?map=/var/www/htdocs/GIS/apps/rainfall/wms.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv?map=/var/www/htdocs/GIS/apps/rainfall/wms.map&amp;"/></Post>
        </HTTP>
      </DCPType>
    </GetMap>
    <GetFeatureInfo>
      <Format>text/plain</Format>
      <Format>text/html</Format>
      <Format>application/vnd.ogc.gml</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv?map=/var/www/htdocs/GIS/apps/rainfall/wms.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv?map=/var/www/htdocs/GIS/apps/rainfall/wms.map&amp;"/></Post>
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
    <Name>radar</Name>
    <Title>IEM RadView WMS Service</Title>
    <SRS>EPSG:26915</SRS>
    <LatLonBoundingBox minx="-96.7539" miny="39.6972" maxx="-90.3709" maxy="44.2532" />
    <BoundingBox SRS="EPSG:26915"
                minx="200000" miny="4.4e+06" maxx="710000" maxy="4.9e+06" />
    <ScaleHint min="44.9013" max="231.9" />
    <Layer queryable="0" opaque="0" cascaded="0">
        <Name>month_rainfall</Name>
        <Title>Rainfall This Month</Title>
        <SRS>EPSG:26915</SRS>
    </Layer>
    <Layer queryable="0" opaque="0" cascaded="0">
        <Name>sevendays_rainfall</Name>
        <Title>Past 7 Days</Title>
        <SRS>EPSG:26915</SRS>
    </Layer>
    <Layer queryable="0" opaque="0" cascaded="0">
        <Name>yesterday_rainfall</Name>
        <Title>Rainfall Yesterday</Title>
        <SRS>EPSG:26915</SRS>
    </Layer>
  </Layer>
</Capability>
</WMT_MS_Capabilities>
