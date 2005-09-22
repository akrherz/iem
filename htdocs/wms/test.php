<?php header("Content-type:application/vnd.ogc.gml"); ?>
<WMT_MS_Capabilities version="1.1.1" updateSequence="0">
<Service> <!-- a service IS a MapServer mapfile -->
  <Name>GetMap</Name> <!-- WMT defined -->
  <Title>Fawkner MapServer</Title>
  <Abstract>Because I have nothing better to do</Abstract>
  <OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://localhost/_cgi-bin/mapserv.exe?map=c:\inetpub\wwwroot\fawkner_mapserv\fawkner_wms.map&amp;"/>
  <ContactInformation>
  </ContactInformation>
  <AccessConstraints>none</AccessConstraints>
</Service>

<Capability>
  <Request>
    <GetCapabilities>
      <Format>application/vnd.ogc.wms_xml</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://localhost/_cgi-bin/mapserv.exe?map=c:\inetpub\wwwroot\fawkner_mapserv\fawkner_wms.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://localhost/_cgi-bin/mapserv.exe?map=c:\inetpub\wwwroot\fawkner_mapserv\fawkner_wms.map&amp;"/></Post>
        </HTTP>
      </DCPType>
    </GetCapabilities>
    <GetMap>
      <Format>image/gif</Format>
      <Format>image/png</Format>
      <Format>image/jpeg</Format>
      <Format>image/wbmp</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://localhost/_cgi-bin/mapserv.exe?map=c:\inetpub\wwwroot\fawkner_mapserv\fawkner_wms.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://localhost/_cgi-bin/mapserv.exe?map=c:\inetpub\wwwroot\fawkner_mapserv\fawkner_wms.map&amp;"/></Post>
        </HTTP>
      </DCPType>
    </GetMap>
    <GetFeatureInfo>
      <Format>text/plain</Format>
      <Format>text/html</Format>
      <Format>application/vnd.ogc.gml</Format>
      <DCPType>
        <HTTP>
          <Get><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://localhost/_cgi-bin/mapserv.exe?map=c:\inetpub\wwwroot\fawkner_mapserv\fawkner_wms.map&amp;"/></Get>
          <Post><OnlineResource xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://localhost/_cgi-bin/mapserv.exe?map=c:\inetpub\wwwroot\fawkner_mapserv\fawkner_wms.map&amp;"/></Post>
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
    <Name>FAWKNER</Name>
    <Title>Fawkner MapServer</Title>
    <SRS>EPSG:4326</SRS>
    <LatLonBoundingBox minx="112.286" miny="-45.0502" maxx="154.857" maxy="-8.52123" />
    <BoundingBox SRS="EPSG:4326"
                minx="112.286" miny="-45.0502" maxx="154.857" maxy="-8.52123" />
    <ScaleHint min="0.498903" max="498903" />
    <Layer queryable="0" opaque="0" cascaded="0">
        <Name>oceansea</Name>
        <Title>CountyoceanseaBoundary</Title>
        <Abstract>Oceans and Seas</Abstract>
        <SRS>EPSG:4326</SRS>
        <LatLonBoundingBox minx="72" miny="-55.9612" maxx="170.731" maxy="-2.10025" />
        <BoundingBox SRS="EPSG:4326"
                    minx="72" miny="-55.9612" maxx="170.731" maxy="-2.10025" />
    </Layer>
  </Layer>
</Capability>
</WMT_MS_Capabilities>
