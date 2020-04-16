<?php
 require_once "../../config/settings.inc.php";
 header("Content-type: application/vnd.ogc.gml");
 $d = isset($_GET["date"]) ? $_GET["date"] : date("Y-m-d");
 $d = isset($_GET["DATE"]) ? $_GET["DATE"] : $d;
 $year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
 $year = isset($_GET["YEAR"]) ? $_GET["YEAR"] : $year;
 $year = substr($year, 0, 4);
 $sts = "$d%2000:00";
 $ets = "$d%2023:59";
 $uri = "https://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.fcgi?map=/opt/iem/data/wfs/ww.map&amp;YEAR=$year&amp;STARTTS=$sts&amp;ENDTS=$ets&amp;";
 if (isset($_GET['time'])){
 	$year = substr($d,0,4);
 	 $ts = "$d%20".$_GET['time'];
 	 $uri = "https://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv.fcgi?map=/opt/iem/data/wfs/wwt.map&amp;YEAR=$year&TS=$ts&amp;";
 }
echo <<<EOF
<wfs:WFS_Capabilities xmlns:gml="http://www.opengis.net/gml" xmlns:wfs="http://www.opengis.net/wfs" xmlns:ows="http://www.opengis.net/ows" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ogc="http://www.opengis.net/ogc" xmlns="http://www.opengis.net/wfs" version="1.1.0" xsi:schemaLocation="http://www.opengis.net/wfs http://schemas.opengis.net/wfs/1.1.0/wfs.xsd">
<ows:ServiceIdentification>
<ows:Title>IEM Weather Warnings</ows:Title>
<ows:Abstract>Archived NWS Watch, Warning, Advisories</ows:Abstract>
<ows:Keywords>
<ows:Keyword>NWS</ows:Keyword>
<ows:Keyword>Warnings</ows:Keyword>
</ows:Keywords>
<ows:ServiceType codeSpace="OGC">OGC WFS</ows:ServiceType>
<ows:ServiceTypeVersion>1.1.0</ows:ServiceTypeVersion>
<ows:Fees>None</ows:Fees>
<ows:AccessConstraints>None</ows:AccessConstraints>
</ows:ServiceIdentification>
<ows:ServiceProvider>
<ows:ProviderName>Iowa State University</ows:ProviderName>
<ows:ProviderSite xlink:type="simple" xlink:href="{$uri}"/>
<ows:ServiceContact>
<ows:IndividualName>Daryl Herzmann</ows:IndividualName>
<ows:PositionName>Assistant Scientist</ows:PositionName>
<ows:ContactInfo>
<ows:Phone>
<ows:Voice>515-294-5978</ows:Voice>
<ows:Facsimile>515-294-5978</ows:Facsimile>
</ows:Phone>
<ows:Address>
<ows:DeliveryPoint>3015 Agronomy Hall</ows:DeliveryPoint>
<ows:City>Ames</ows:City>
<ows:AdministrativeArea>Iowa</ows:AdministrativeArea>
<ows:PostalCode>50014</ows:PostalCode>
<ows:Country>USA</ows:Country>
<ows:ElectronicMailAddress>akrherz@iastate.edu</ows:ElectronicMailAddress>
</ows:Address>
<ows:OnlineResource xlink:type="simple" xlink:href="{$uri}"/>
<ows:HoursOfService>24x7</ows:HoursOfService>
<ows:ContactInstructions>email</ows:ContactInstructions>
</ows:ContactInfo>
<ows:Role>Owner</ows:Role>
</ows:ServiceContact>
</ows:ServiceProvider>
<ows:OperationsMetadata>
<ows:Operation name="GetCapabilities">
<ows:DCP>
<ows:HTTP>
<ows:Get xlink:type="simple" xlink:href="{$uri}"/>
<ows:Post xlink:type="simple" xlink:href="{$uri}"/>
</ows:HTTP>
</ows:DCP>
<ows:Parameter name="service">
<ows:Value>WFS</ows:Value>
</ows:Parameter>
<ows:Parameter name="AcceptVersions">
<ows:Value>1.0.0</ows:Value>
<ows:Value>1.1.0</ows:Value>
</ows:Parameter>
<ows:Parameter name="AcceptFormats">
<ows:Value>text/xml</ows:Value>
</ows:Parameter>
</ows:Operation>
<ows:Operation name="DescribeFeatureType">
<ows:DCP>
<ows:HTTP>
<ows:Get xlink:type="simple" xlink:href="{$uri}"/>
<ows:Post xlink:type="simple" xlink:href="{$uri}"/>
</ows:HTTP>
</ows:DCP>
<ows:Parameter name="outputFormat">
<ows:Value>XMLSCHEMA</ows:Value>
<ows:Value>text/xml; subtype=gml/2.1.2</ows:Value>
<ows:Value>text/xml; subtype=gml/3.1.1</ows:Value>
</ows:Parameter>
</ows:Operation>
<ows:Operation name="GetFeature">
<ows:DCP>
<ows:HTTP>
<ows:Get xlink:type="simple" xlink:href="{$uri}"/>
<ows:Post xlink:type="simple" xlink:href="{$uri}"/>
</ows:HTTP>
</ows:DCP>
<ows:Parameter name="resultType">
<ows:Value>results</ows:Value>
<ows:Value>hits</ows:Value>
</ows:Parameter>
<ows:Parameter name="outputFormat">
<ows:Value>text/xml; subtype=gml/3.1.1</ows:Value>
</ows:Parameter>
</ows:Operation>
</ows:OperationsMetadata>
<FeatureTypeList>
<Operations>
<Operation>Query</Operation>
</Operations>
<FeatureType>
<Name>counties</Name>
<Title>Iowa Counties</Title>
<DefaultSRS>urn:ogc:def:crs:EPSG::4326</DefaultSRS>
<OutputFormats>
<Format>text/xml; subtype=gml/3.1.1</Format>
</OutputFormats>
<ows:WGS84BoundingBox dimensions="2">
<ows:LowerCorner>-96.640709192144 40.3719466182637</ows:LowerCorner>
<ows:UpperCorner>-90.1427967503368 43.5014574340012</ows:UpperCorner>
</ows:WGS84BoundingBox>
</FeatureType>
<FeatureType>
<Name>archwarn_county</Name>
<Title>County Based Warnings</Title>
<DefaultSRS>urn:ogc:def:crs:EPSG::4326</DefaultSRS>
<OutputFormats>
<Format>text/xml; subtype=gml/3.1.1</Format>
</OutputFormats>
<ows:WGS84BoundingBox/>
<!--
WARNING: Optional WGS84BoundingBox could not be established for this layer.  Consider setting the EXTENT in the LAYER object, or wfs_extent metadata. Also check that your data exists in the DATA statement
-->
</FeatureType>
<FeatureType>
<Name>archwarn_polygon</Name>
<Title>Polygon Based Warnings</Title>
<DefaultSRS>urn:ogc:def:crs:EPSG::4326</DefaultSRS>
<OutputFormats>
<Format>text/xml; subtype=gml/3.1.1</Format>
</OutputFormats>
<ows:WGS84BoundingBox/>
<!--
WARNING: Optional WGS84BoundingBox could not be established for this layer.  Consider setting the EXTENT in the LAYER object, or wfs_extent metadata. Also check that your data exists in the DATA statement
-->
</FeatureType>
<FeatureType>
<Name>warn_polygon</Name>
<Title>Current Polygon Based Warnings</Title>
<DefaultSRS>urn:ogc:def:crs:EPSG::4326</DefaultSRS>
<OutputFormats>
<Format>text/xml; subtype=gml/3.1.1</Format>
</OutputFormats>
<ows:WGS84BoundingBox/>
<!--
WARNING: Optional WGS84BoundingBox could not be established for this layer.  Consider setting the EXTENT in the LAYER object, or wfs_extent metadata. Also check that your data exists in the DATA statement
-->
</FeatureType>
<FeatureType>
<Name>warn_county</Name>
<Title>Current County Based Warnings</Title>
<DefaultSRS>urn:ogc:def:crs:EPSG::4326</DefaultSRS>
<OutputFormats>
<Format>text/xml; subtype=gml/3.1.1</Format>
</OutputFormats>
<ows:WGS84BoundingBox/>
<!--
WARNING: Optional WGS84BoundingBox could not be established for this layer.  Consider setting the EXTENT in the LAYER object, or wfs_extent metadata. Also check that your data exists in the DATA statement
-->
</FeatureType>
</FeatureTypeList>
<ogc:Filter_Capabilities>
<ogc:Spatial_Capabilities>
<ogc:GeometryOperands>
<ogc:GeometryOperand>gml:Point</ogc:GeometryOperand>
<ogc:GeometryOperand>gml:LineString</ogc:GeometryOperand>
<ogc:GeometryOperand>gml:Polygon</ogc:GeometryOperand>
<ogc:GeometryOperand>gml:Envelope</ogc:GeometryOperand>
</ogc:GeometryOperands>
<ogc:SpatialOperators>
<ogc:SpatialOperator name="Equals"/>
<ogc:SpatialOperator name="Disjoint"/>
<ogc:SpatialOperator name="Touches"/>
<ogc:SpatialOperator name="Within"/>
<ogc:SpatialOperator name="Overlaps"/>
<ogc:SpatialOperator name="Crosses"/>
<ogc:SpatialOperator name="Intersects"/>
<ogc:SpatialOperator name="Contains"/>
<ogc:SpatialOperator name="DWithin"/>
<ogc:SpatialOperator name="Beyond"/>
<ogc:SpatialOperator name="BBOX"/>
</ogc:SpatialOperators>
</ogc:Spatial_Capabilities>
<ogc:Scalar_Capabilities>
<ogc:LogicalOperators/>
<ogc:ComparisonOperators>
<ogc:ComparisonOperator>LessThan</ogc:ComparisonOperator>
<ogc:ComparisonOperator>GreaterThan</ogc:ComparisonOperator>
<ogc:ComparisonOperator>LessThanEqualTo</ogc:ComparisonOperator>
<ogc:ComparisonOperator>GreaterThanEqualTo</ogc:ComparisonOperator>
<ogc:ComparisonOperator>EqualTo</ogc:ComparisonOperator>
<ogc:ComparisonOperator>NotEqualTo</ogc:ComparisonOperator>
<ogc:ComparisonOperator>Like</ogc:ComparisonOperator>
<ogc:ComparisonOperator>Between</ogc:ComparisonOperator>
</ogc:ComparisonOperators>
</ogc:Scalar_Capabilities>
<ogc:Id_Capabilities>
<ogc:EID/>
<ogc:FID/>
</ogc:Id_Capabilities>
</ogc:Filter_Capabilities>
</wfs:WFS_Capabilities>
EOF;
?>