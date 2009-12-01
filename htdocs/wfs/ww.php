<?php
  header("Content-type: application/vnd.ogc.gml");
 $d = isset($_GET["date"]) ? $_GET["date"] : date("Y-m-d");
 $year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
 $year = substr($year, 0, 4);
 $sts = "$d%2000:00";
 $ets = "$d%2023:59";
 $uri = "http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv?map=/var/www/data/wfs/ww.map&amp;year=$year&amp;startts=$sts&amp;endts=$ets&amp;";
 ?>
<WFS_Capabilities
   version="1.0.0"
   updateSequence="0"
   xmlns="http://www.opengis.net/wfs"
   xmlns:ogc="http://www.opengis.net/ogc"
   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengeospatial.net/wfs/1.0.0/WFS-capabilities.xsd">

<!-- MapServer version 4.4.0 OUTPUT=GIF OUTPUT=PNG OUTPUT=JPEG OUTPUT=WBMP SUPPORTS=PROJ SUPPORTS=FREETYPE SUPPORTS=WMS_SERVER SUPPORTS=WMS_CLIENT SUPPORTS=WFS_SERVER INPUT=EPPL7 INPUT=POSTGIS INPUT=OGR INPUT=GDAL INPUT=SHAPEFILE -->

<Service>
  <Name>MapServer WFS</Name>
  <Title>IEM Weather Warnings</Title>
  <Abstract>Ba Ba Ba</Abstract>
  <Keywords>Ba Ba Ba</Keywords>
  <Fees>NONE</Fees>
  <OnlineResource>
   <?php echo $uri; ?>
  </OnlineResource>
  <AccessConstraints>None</AccessConstraints>
</Service>

<Capability>
  <Request>
    <GetCapabilities>
      <DCPType>
        <HTTP>
          <Get onlineResource="<?php echo $uri; ?>" />
        </HTTP>
      </DCPType>
      <DCPType>
        <HTTP>
          <Post onlineResource="<?php echo $uri; ?>" />
        </HTTP>
      </DCPType>
    </GetCapabilities>
    <DescribeFeatureType>
      <SchemaDescriptionLanguage>
        <XMLSCHEMA/>
      </SchemaDescriptionLanguage>
      <DCPType>
        <HTTP>
          <Get onlineResource="<?php echo $uri; ?>" />
        </HTTP>
      </DCPType>
      <DCPType>
        <HTTP>
          <Post onlineResource="<?php echo $uri; ?>" />
        </HTTP>
      </DCPType>
    </DescribeFeatureType>
    <GetFeature>
      <ResultFormat>
        <GML2/>
      </ResultFormat>
      <DCPType>
        <HTTP>
          <Get onlineResource="<?php echo $uri; ?>" />
        </HTTP>
      </DCPType>
      <DCPType>
        <HTTP>
          <Post onlineResource="<?php echo $uri; ?>" />
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
        <Name>counties</Name>
        <Title>Iowa Counties</Title>
        <SRS>EPSG:4326</SRS>
        <LatLongBoundingBox minx="-96.6407" miny="40.3719" maxx="-90.1428" maxy="43.5015" />
    </FeatureType>
    <FeatureType>
        <Name>archwarn_county</Name>
        <Title>County Based Warnings</Title>
        <SRS>EPSG:4326</SRS>
        <LatLongBoundingBox minx="-170.0" miny="10.0" maxx="-30.0" maxy="80.0" />
    </FeatureType>
    <FeatureType>
        <Name>archwarn_polygon</Name>
        <Title>Polygon Based Warnings</Title>
        <SRS>EPSG:4326</SRS>
        <LatLongBoundingBox minx="-170.0" miny="10.0" maxx="-30.0" maxy="80.0" />
    </FeatureType>
    <FeatureType>
        <Name>warn_polygon</Name>
        <Title>Current Polygon Based Warnings</Title>
        <SRS>EPSG:4326</SRS>
        <LatLongBoundingBox minx="-170.0" miny="10.0" maxx="-30.0" maxy="80.0" />
    </FeatureType>
    <FeatureType>
        <Name>warn_county</Name>
        <Title>Current County Based Warnings</Title>
        <SRS>EPSG:4326</SRS>
        <LatLongBoundingBox minx="-170.0" miny="10.0" maxx="-30.0" maxy="80.0" />
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
