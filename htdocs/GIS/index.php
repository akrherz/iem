<?php
include("../../config/settings.inc.php");
$TITLE = "IEM | GIS Homepage";
$THISPAGE = "gis";
include("$rootpath/include/header.php"); ?>


<h3 class="heading">IEM GIS Information</h3>
<div class="text">

<p>Geographic Information System (GIS) is a system for manipulating spatially 
referenced data.  Since the IEM contains many spatially referenced datasets, it would only seem
natural to integrate IEM data into GIS applications.<p>

<table border=0 width=100%>
<tr><td width=350 valign="top">

<h3 class="subtitle">Presentations & Docs:</h3>
<ul>
 <li><i>28 Jul 2003:</i> <a href="/docs/radmapserver/">NEXRAD + Mapserver HOWTO</a>
<br />A HowTo on generating NEXRAD composite images with GEMPAK and 
serving them out with Mapserver.</li>
 <li><a href="<?php echo $rooturl; ?>/present/">IEM Presentation Archive</a>
<br />The IEM has given a number of GIS related talks.  You can browse an
archive of presentations.</li>
</ul>


<p><h3 class="subtitle">Web Applications:</h3>
<ul>
<!--
  <LI><a href="/cgi-bin/mapserv/mapserv?map=/var/www/htdocs/GIS%2Fapps%2Fiatorn%2Fiatorn.map">Historical Iowa Tornado Database</a></LI>
  <LI><a href="/GIS/apps/precip/">Realtime Precipitation Analysis</a></LI>
  <LI><a href="<?php echo $rooturl; ?>/GIS/apps/pcs/">2002 NEXRAD vs ASOS Precip Comparison</a></LI>
-->
  <li><a href="<?php echo $rooturl; ?>/GIS/apps/rview/warnings.phtml">NEXRAD w/ warnings</a></li>
  <li><a href="<?php echo $rooturl; ?>/GIS/apps/coop/">COOP Daily Extremes and Averages</a></li>
  <li><a href="<?php echo $rooturl; ?>/my/current.php">Dynamic Plotting</a></li>
  <li><a href="<?php echo $rooturl; ?>/sites/locate.php">IEM Site Locator</a></li>
</ul>


<p><h3 class="subtitle">Links:</h3>
<ul>
 <li><a href="http://drought.unl.edu/dm/dmshps_archive.htm">US Drought Monitor GIS data</a>
  <br />Download current and historical drought monitor products in GIS formats</li>
 <li><a href="http://www.spc.noaa.gov/gis/svrgis/">GIS Severe Weather reports</a>
 <br />Archive of NCDC provided storm reports!</li>
 <li><a href="http://gis.ncdc.noaa.gov/aimstools/gis.jsp">NCDC GIS Portal</a><br />National Climate Data Center GIS goodies</li>
 <li><a href="http://wdssii.nssl.noaa.gov/geotiff/">NSSL Google Earth Data</a>
  <br />Weather data integrated into Google Earth!</li>
 <li><a href="http://www.ocs.orst.edu/prism/products/matrix.phtml">Oregon State PRISM</a>
	<br />These folks provide nationwide GIS ready datasets of climate data.  Their site is outstanding!</li>
 <li><a href="/GIS/software.php">GIS Software</a></li>
 <li>Scott Shipley's <a href="http://geog.gmu.edu/projects/wxproject/nex2shp/nexrad.htm">NEXRAD to shapefile</a> converter.
 <li><a href="http://www.ftw.nrcs.usda.gov/prism/prism.html">USDA PRISM</a> data page (GIS Climate Data).</li>
 <li>Iowa <a href="http://www.igsb.uiowa.edu/nrgis/gishome.htm">Natural Resources Geographic Information System (NRGIS)</a></li>
 <li>NOAA's Ken Waters work with <a href="http://www.weather.gov/regsci/gis/">GIS and NWS warnings</a><br />They have some historical GIS datasets of warnings too.</li>
 <li><a href="http://pnwpest.org/US/index.html">Index to Degree-Day Data</a></li>
 <li><a href="http://map06.gsfc.nasa.gov/">NASA MAP'06 program</a>
  <br />Has some GIS satellite data.</li>
</ul>

</td><td width=350 valign="top">

<img src="<?php echo $rooturl; ?>/images/gisready.png">You may have noticed this image appearing on
IEM webpages.  It signifies that the data link is ready for most GIS systems.

<p><h3 class="subtitle">IEM GIS Projects</h3>
<ul>
 <li><a href="goes.phtml">GOES Satellite GIS Products</a>
  <br />Current and archived GIS products from NOAA's GOES satellites</li>
 <li><a href="<?php echo $rooturl; ?>/ogc/">Open GIS Web Services</a>
  <br />A listing of OGC web services offered by the IEM</li>
 <li><a href="/climodat/index.phtml#ks">Iowa Climate Summaries</a>
  <br />GIS ready data files of monthly and yearly climate summaries dating
back to 1951.</li>
	<li><a href="<?php echo $rooturl; ?>/GIS/apps/iem/freeze.phtml">IEM Freeze</a>
	<br />Web mapping application to support winter weather nowcasting.</li>
	<li><a href="<?php echo $rooturl; ?>/GIS/radview.phtml">IEM Radview</a>
	<br />Our effort to provide NEXRAD information in realtime to GIS systems.</li>
 <li><a href="<?php echo $rooturl; ?>/rainfall/">IEM Rainfall</a>
  <br />Gridded rainfall estimates in GIS formats dating back to 2002 for Iowa.</li>
 <li><a href="<?php echo $rooturl; ?>/roads/">IEM Iowa Road Conditions</a>
  <br />Current and archived Iowa road conditions.</li>
 <li><a href="<?php echo $rooturl; ?>/cow/">IEM Cow</a>
  <br />Unofficial NWS polygon warning verification.</li>
 <li><a href="<?php echo $rooturl; ?>/docs/nexrad_composites/">NEXRAD Composites on the IEM</a>
  <br />Information about the NEXRAD composites that the IEM generates.</li>
</ul>

<p><h3 class="subtitle">GIS Shapefiles:</h3>
<ul>
 <li><a href="datasets/iaclimate.zip">1970-2000 Iowa Climate</a>
  <br>1970-2000 average annual precipitation, average temperature as 
    calculated from the IEM databases.</li>
 <li><a href="/data/gis/shape/4326/us/lsr_24hour.zip">Past 24 hours of Storm Reports</a>
 <br />A shapefile of Local Storm Reports (LSRs) valid for the past 24 hours.  The file is updated every 5 minutes.</li>
 <li><a href="/request/gis/lsrs.phtml">Archived Local Storm Reports</a>
 <br />Generate a shapefile of LSRs for a period of your choice dating back 
  to 2003!</li>
 <li><a href="/data/gis/shape/4326/us/current_ww.zip">Current NWS Warnings</a>
 <br />A shapefile of active county based and polygon based weather warnings. 
This file is updated every 5 minutes.</li>
 <li><a href="/request/gis/watchwarn.phtml">Archived NWS Warnings</a>
 <br />Generate a shapefile of weather warnings for a time period of your
 choice!</li>

 <li><a href="/data/gis/shape/4326/us/current_nexattr.zip">Current NEXRAD Storm Attributes</a>
  <br />Point shapefile generated every minute containing a summary of
   NEXRAD storm attributes.</li>
 <li><a href="/data/gis/shape/4326/iem/coopobs.zip">NWS COOP Observations</a>
   <br>Today's climate reports</li>
 <li><a href="/data/gis/">Browse</a> GIS data stored on the IEM website.</li>
</ul>

</td></tr></table>
<br><br></div>

<?php include("$rootpath/include/footer.php"); ?>
