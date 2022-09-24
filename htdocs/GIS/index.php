<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "GIS Mainpage";
$t->content = <<<EOM

<h3>IEM GIS Information</h3>


<p>Geographic Information System (GIS) is a system for manipulating spatially 
referenced data.  Since the IEM contains many spatially referenced datasets, it would only seem
natural to integrate IEM data into GIS applications.<p>

<div class="row">
<div class="col-md-6">

<h3>Presentations & Docs:</h3>
<ul>
 <li><i>28 Jul 2003:</i> <a href="/docs/radmapserver/">NEXRAD + Mapserver HOWTO</a>
<br />A HowTo on generating NEXRAD composite images with GEMPAK and 
serving them out with Mapserver.</li>
 <li><a href="/present/">IEM Presentation Archive</a>
<br />The IEM has given a number of GIS related talks.  You can browse an
archive of presentations.</li>
 <li><a href="rasters.php">IEM RASTERs Lookup Tables</a>
<br />Metadata on how you can convert IEM produced RASTERs into actual
        values!</li>
</ul>


<p><h3>Web Applications:</h3>
<ul>
    <li><a href="/GIS/apps/rview/warnings.phtml">NEXRAD w/ warnings</a></li>
    <li><a href="/GIS/apps/coop/">COOP Daily Extremes and Averages</a></li>
    <li><a href="/my/current.php">Dynamic Plotting</a></li>
    <li><a href="/sites/locate.php">IEM Site Locator</a></li>
    <li><a href="rad-by-year-fe.phtml">NEXRAD Mosaic by Year</a>
    <br />Displays NEXRAD mosaicked base reflectivity for a user specified
    sector for the same time each year going back to 1995.</li>
</ul>


<p><h3>Links:</h3>
<ul>
 <li><a href="http://droughtmonitor.unl.edu/MapsAndData.aspx">US Drought Monitor GIS data</a>
  <br />Download current and historical drought monitor products in GIS formats</li>
 <li><a href="http://www.ncdc.noaa.gov/swdi/">NCDC Severe Weather Data Inventory</a>
 <br />A tremendous website with lots of hard to find data!</li>
 <li><a href="http://www.spc.noaa.gov/gis/svrgis/">GIS Severe Weather reports</a>
 <br />Archive of NCDC provided storm reports (1950-)!</li>
 <li><a href="https://gis.ncdc.noaa.gov/map/viewer/#app=cdo">NCDC GIS Portal</a><br />National Climate Data Center GIS goodies</li>

 <li>NCEI's <a href="https://www.ncdc.noaa.gov/data-access/radar-data/radar-display-tools">Display and Conversion Tools</a>.</li>

 <li><a href="http://wdssii.nssl.noaa.gov/?r=products">NSSL Google Earth Data</a>
  <br />Weather data integrated into Google Earth!</li>
 <li><a href="http://www.ocs.orst.edu/prism/products/matrix.phtml">Oregon State PRISM</a>
    <br />These folks provide nationwide GIS ready datasets of climate data.  Their site is outstanding!</li>
  
  <li><a href="http://www.prism.oregonstate.edu/">USDA PRISM</a> data page (GIS Climate Data).</li>
 <li>Iowa <a href="http://www.igsb.uiowa.edu/nrgis/gishome.htm">Natural Resources Geographic Information System (NRGIS)</a></li>
 <li>NOAA's Ken Waters work with <a href="http://www.weather.gov/regsci/gis/">GIS and NWS warnings</a><br />They have some historical GIS datasets of warnings too.</li>
 <li><a href="http://pnwpest.org/US/index.html">Index to Degree-Day Data</a></li>
 <li><a href="http://map.nasa.gov/MAP06/">NASA MAP'06 program</a>
  <br />Has some GIS satellite data.</li>
</ul>

</div>
<div class="col-md-6">

<img src="/images/gisready.png">You may have noticed this image appearing on
IEM webpages.  It signifies that the data link is ready for most GIS systems.

<p><h3>IEM GIS Projects</h3>
<ul>
 <li><a href="goes.phtml">GOES Satellite GIS Products</a>
  <br />Current and archived GIS products from NOAA's GOES satellites</li>
 <li><a href="/ogc/">Open GIS Web Services</a>
  <br />A listing of OGC web services offered by the IEM</li>
 <li><a href="/climodat/index.phtml#ks">Iowa Climate Summaries</a>
  <br />GIS ready data files of monthly and yearly climate summaries dating
back to 1951.</li>
    <li><a href="/GIS/apps/iem/freeze.phtml">IEM Freeze</a>
    <br />Web mapping application to support winter weather nowcasting.</li>
    <li><a href="/GIS/radview.phtml">IEM Radview</a>
    <br />Our effort to provide NEXRAD information in realtime to GIS systems.</li>
 <li><a href="/rainfall/">IEM Rainfall</a>
  <br />Gridded rainfall estimates in GIS formats dating back to 2002 for Iowa.</li>
 <li><a href="/roads/">IEM Iowa Road Conditions</a>
  <br />Current and archived Iowa road conditions.</li>
 <li><a href="/cow/">IEM Cow</a>
  <br />Unofficial NWS polygon warning verification.</li>
 <li><a href="/docs/nexrad_mosiac/">NEXRAD Mosiac on the IEM</a>
  <br />Information about the NEXRAD Mosiac that the IEM generates.</li>
</ul>

<p><h3>GIS Shapefiles:</h3>
<ul>
<li><a href="/request/gis/spc_mcd.phtml"><i class="fa fa-download"></i>
SPC Mesoscale Discussion Shapefile Download</a></li>

<li><a href="/request/gis/spc_outlooks.phtml"><i class="fa fa-download"></i> SPC Outlook Shapefile Download</a></li>

<li><a href="/request/gis/spc_watch.phtml"><i class="fa fa-download"></i>
SPC Watch Polygon Shapefile Download</a></li>

<li>Past 24 hours of Storm Reports
 <br /><a href="/data/gis/shape/4326/us/lsr_24hour.zip">ESRI Shapefile</a>, 
 <a href="/data/gis/shape/4326/us/lsr_24hour.csv">Comma Delimited</a>,
 <a href="/data/gis/shape/4326/us/lsr_24hour.geojson">GeoJSON</a>
 <br />The IEM parses the realtime feed of NWS Local Storm Reports.  Every
 5 minutes, a process collects up the last 24 hours worth of reports and
 dumps them to the above files.</li>
 
 <li><a href="/request/gis/lsrs.phtml">Archived Local Storm Reports</a>
 <br />Generate a shapefile of LSRs for a period of your choice dating back 
  to 2003!</li>
 <li><a href="/data/gis/shape/4326/us/current_ww.zip">Current NWS Warnings</a>
 <br />A shapefile of active county based and polygon based weather warnings. 
This file is updated every minute.</li>
 <li><a href="/request/gis/watchwarn.phtml">Archived NWS Warnings</a>
 <br />Generate a shapefile of weather warnings for a time period of your
 choice!</li>

 <li><a href="/data/gis/shape/4326/us/current_nexattr.zip">Current NEXRAD Storm Attributes</a>
  <br />Point shapefile generated every minute containing a summary of
   NEXRAD storm attributes.</li>
 <li><a href="/request/gis/nexrad_storm_attrs.php">Archived NEXRAD Storm Attributes</a>
 <br />Generate a shapefile of storm attributes for a RADAR and time period
 of your choice from the archive.</li>
 <li><a href="/data/gis/shape/4326/iem/coopobs.zip">NWS COOP Observations</a>
   <br>Today's climate reports</li>
 <li><a href="/request/gis/sps.phtml">Special Weather Statement (SPS) Polygons</a><br />
 Shapefile download of SPS polygons and IBW tags.</li>
 <li><a href="/data/gis/">Browse</a> GIS data stored on the IEM website.</li>

 <li><a href="/request/gis/wpc_mpd.phtml"><i class="fa fa-download"></i>
WPC Precip Discussion MPD Polygon Shapefile Download</a></li>

 </ul>

</div></div>
EOM;
$t->render("single.phtml");
