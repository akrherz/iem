<?php
  header("Content-type: application/vnd.ogc.gml");
 ?>
<WFS_Capabilities xmlns="http://www.opengis.net/wfs" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0"> 

<!-- MapServer version 4.2.0 OUTPUT=PNG OUTPUT=JPEG OUTPUT=WBMP SUPPORTS=PROJ SUPPORTS=FREETYPE SUPPORTS=WMS_SERVER SUPPORTS=WFS_SERVER INPUT=EPPL7 INPUT=POSTGIS INPUT=OGR INPUT=GDAL INPUT=SHAPEFILE -->
 
<Service>
  <Name>WFS</Name>
  <Title>IEM WMS Service</Title>
  <Abstract>Ba Ba Ba</Abstract>
  <Keywords>
    Ba
  </Keywords>
  <OnlineResource>http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.420?map=/var/www/htdocs/GIS/apps/rainfall/rainfall.map&amp;amp;&amp;</OnlineResource>
  <Fees>None</Fees>
  <AccessConstraints>None</AccessConstraints>
</Service>
 
<Capability>
  <Request>
    <GetCapabilities>
      <DCPType>
        <HTTP>
          <Get onlineResource="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.420?map=/var/www/htdocs/GIS/apps/rainfall/rainfall.map&amp;amp;&amp;" />
        </HTTP>
      </DCPType>
      <DCPType>
        <HTTP>
          <Post onlineResource="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.420?map=/var/www/htdocs/GIS/apps/rainfall/rainfall.map&amp;amp;&amp;" />
        </HTTP>
      </DCPType>
    </GetCapabilities>
    <DescribeFeatureType>
      <SchemaDescriptionLanguage>
        <XMLSCHEMA />
      </SchemaDescriptionLanguage>
      <DCPType>
        <HTTP>
<Get onlineResource=" http://star.esri.com/wfsconnector/com.esri.wsit.WFSServlet/TEST_SERVICE?" />
        </HTTP>
      </DCPType>
      <DCPType>
        <HTTP>
<Post onlineResource=" http://star.esri.com/wfsconnector/com.esri.wsit.WFSServlet/TEST_SERVICE?" />
        </HTTP>
      </DCPType>
    </DescribeFeatureType>
    <GetFeature>
      <ResultFormat>
        <GML2/>
      </ResultFormat>
      <DCPType>
        <HTTP>
          <Get onlineResource="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.420?map=/var/www/htdocs/GIS/apps/rainfall/rainfall.map&amp;amp;&amp;" />
        </HTTP>
      </DCPType>
      <DCPType>
        <HTTP>
          <Post onlineResource="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.420?map=/var/www/htdocs/GIS/apps/rainfall/rainfall.map&amp;amp;&amp;" />
        </HTTP>
      </DCPType>
    </GetFeature>
  </Request>
</Capability>
 
<FeatureTypeList>
  <Operations>
    <Query/>
  </Operations>
    <FeatureType>
        <Name>month_rainfall</Name>
        <Title>Rainfall This Month</Title>
        <Abstract>Ba</Abstract>
        <Keywords>
          Ba
        </Keywords>
        <SRS>EPSG:26915</SRS>
        <LatLongBoundingBox minx="-175.959" miny="-8.2419e+12" maxx="173.59" maxy="8.2419e+12" />
    </FeatureType>
    <FeatureType>
        <Name>counties</Name>
        <Title>Iowa Counties</Title>
        <SRS>EPSG:26915</SRS>
        <LatLongBoundingBox minx="-96.6849" miny="40.3328" maxx="-90.0694" maxy="43.557" />
    </FeatureType>
</FeatureTypeList>
 
<ogc:Filter_Capabilities>
  <ogc:Spatial_Capabilities>
    <ogc:Spatial_Operators>
      <ogc:Intersect/>
      <ogc:DWithin/>
      <ogc:BBOX/>
    </ogc:Spatial_Operators>
  </ogc:Spatial_Capabilities>
  <ogc:Scalar_Capabilities>
    <ogc:Logical_Operators />
    <ogc:Comparison_Operators>
      <ogc:Simple_Comparisons />
      <ogc:Like />
      <ogc:Between />
    </ogc:Comparison_Operators>
  </ogc:Scalar_Capabilities>
</ogc:Filter_Capabilities>
 
</WFS_Capabilities>

