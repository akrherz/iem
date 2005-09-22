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
  <Title>IEM RadView WMS Service</Title>
  <Abstract>IEM WMS RadView Service</Abstract>
  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.radar?map=/mesonet/www/html/GIS/apps/wms/compradar.map&amp;"/>
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
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.radar?map=/mesonet/www/html/GIS/apps/wms/compradar.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.radar?map=/mesonet/www/html/GIS/apps/wms/compradar.map&amp;"/></Post>
        </HTTP>
      </DCPType>
    </GetCapabilities>
    <GetMap>
      <Format>image/png</Format>
      <Format>image/jpeg</Format>
      <Format>image/wbmp</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.radar?map=/mesonet/www/html/GIS/apps/wms/compradar.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.radar?map=/mesonet/www/html/GIS/apps/wms/compradar.map&amp;"/></Post>
        </HTTP>
      </DCPType>
    </GetMap>
    <GetFeatureInfo>
      <Format>text/plain</Format>
      <Format>text/html</Format>
      <Format>application/vnd.ogc.gml</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.radar?map=/mesonet/www/html/GIS/apps/wms/compradar.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.radar?map=/mesonet/www/html/GIS/apps/wms/compradar.map&amp;"/></Post>
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
   <SRS>EPSG:4326 EPSG:26915 EPSG:26975 EPSG:26976 EPSG:26916 EPSG:26775 EPSG:26776</SRS>
    <LatLonBoundingBox minx="-126" miny="24" maxx="-66" maxy="50" />
    <BoundingBox SRS="EPSG:4326"
                minx="-126" miny="24" maxx="-66" maxy="50" />
    <ScaleHint min="44.9013" max="2319.9" />
    <Layer queryable="0" opaque="0" cascaded="0">
        <Name>nexrad</Name>
        <Title>NEXRAD BASECOMP</Title>
        <SRS>EPSG:4326 EPSG:26915 EPSG:26975 EPSG:26976 EPSG:26916 EPSG:26775 EPSG:26776</SRS>
    </Layer>
    <Layer queryable="0" opaque="0" cascaded="0">
        <Name>uscomp_n1p</Name>
        <Title>NEXRAD 1HR PRECIP</Title>
        <SRS>EPSG:4326 EPSG:26915 EPSG:26975 EPSG:26976 EPSG:26916 EPSG:26775 EPSG:26776</SRS>
    </Layer>
    <Layer queryable="0" opaque="0" cascaded="0">
        <Name>uscomp_ntp</Name>
        <Title>NEXRAD STORM TOTAL</Title>
        <SRS>EPSG:4326 EPSG:26915 EPSG:26975 EPSG:26976 EPSG:26916 EPSG:26775 EPSG:26776</SRS>
    </Layer>
  </Layer>
</Capability>
</WMT_MS_Capabilities>
