<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "GIS Mainpage";
$t->content = <<<EOM

<nav aria-label="breadcrumb">
    <ol class="breadcrumb mb-4">
        <li class="breadcrumb-item active" aria-current="page">GIS Mainpage</li>
    </ol>
</nav>

<div class="mb-4">
    <h1 class="h3 mb-3">IEM GIS Information</h1>

    <p class="lead mb-0">Geographic Information System (GIS) is a system for manipulating spatially
    referenced data. Since the IEM contains many spatially referenced datasets, it is natural to
    integrate IEM data into GIS applications.</p>
</div>

<div class="row g-4">
<div class="col-lg-6">

<div class="card mb-4">
<div class="card-body">

<h2 class="h5 card-title">Presentations &amp; Docs</h2>
<ul class="list-group list-group-flush">
 <li class="list-group-item px-0">
  <div><a href="/docs/radmapserver/">NEXRAD + Mapserver HOWTO</a></div>
  <div class="small text-muted"><i>28 Jul 2003</i> A HowTo on generating NEXRAD composite images with GEMPAK and
  serving them out with Mapserver.</div>
 </li>
 <li class="list-group-item px-0">
  <div><a href="/present/">IEM Presentation Archive</a></div>
  <div class="small text-muted">The IEM has given a number of GIS related talks. You can browse an
  archive of presentations.</div>
 </li>
 <li class="list-group-item px-0">
  <div><a href="rasters.php">IEM RASTERs Lookup Tables</a></div>
  <div class="small text-muted">Metadata on how you can convert IEM produced RASTERs into actual
  values.</div>
 </li>
</ul>

</div>
</div>


<div class="card mb-4">
<div class="card-body">

<h2 class="h5 card-title">Web Applications</h2>
<ul class="list-group list-group-flush">
    <li class="list-group-item px-0"><a href="/GIS/apps/rview/warnings.phtml">NEXRAD w/ warnings</a></li>
    <li class="list-group-item px-0"><a href="/GIS/apps/coop/">COOP Daily Extremes and Averages</a></li>
    <li class="list-group-item px-0"><a href="/my/current.php">Dynamic Plotting</a></li>
    <li class="list-group-item px-0"><a href="/sites/locate.php">IEM Site Locator</a></li>
    <li class="list-group-item px-0">
        <div><a href="rad-by-year-fe.phtml">NEXRAD Mosaic by Year</a></div>
        <div class="small text-muted">Displays NEXRAD mosaicked base reflectivity for a user specified
        sector for the same time each year going back to 1995.</div>
    </li>
</ul>

</div>
</div>


<div class="card">
<div class="card-body">

<h2 class="h5 card-title">Links</h2>
<ul class="list-group list-group-flush">
 <li class="list-group-item px-0"><a href="https://droughtmonitor.unl.edu/MapsAndData.aspx">US Drought Monitor GIS data</a>
  <div class="small text-muted">Download current and historical drought monitor products in GIS formats.</div></li>
 <li class="list-group-item px-0"><a href="https://www.ncdc.noaa.gov/swdi/">NCDC Severe Weather Data Inventory</a>
 <div class="small text-muted">A tremendous website with lots of hard to find data.</div></li>
 <li class="list-group-item px-0"><a href="https://www.spc.noaa.gov/gis/svrgis/">GIS Severe Weather reports</a>
 <div class="small text-muted">Archive of NCDC provided storm reports (1950-).</div></li>
 <li class="list-group-item px-0"><a href="https://gis.ncdc.noaa.gov/map/viewer/#app=cdo">NCDC GIS Portal</a>
 <div class="small text-muted">National Climate Data Center GIS goodies.</div></li>

 <li class="list-group-item px-0">NCEI's <a href="https://www.ncdc.noaa.gov/data-access/radar-data/radar-display-tools">Display and Conversion Tools</a>.</li>

 <li class="list-group-item px-0"><a href="https://wdssii.nssl.noaa.gov/?r=products">NSSL Google Earth Data</a>
  <div class="small text-muted">Weather data integrated into Google Earth.</div></li>
 <li class="list-group-item px-0"><a href="https://www.ocs.orst.edu/prism/products/matrix.phtml">Oregon State PRISM</a>
    <div class="small text-muted">These folks provide nationwide GIS ready datasets of climate data. Their site is outstanding.</div></li>

  <li class="list-group-item px-0"><a href="https://www.prism.oregonstate.edu/">USDA PRISM</a> data page (GIS Climate Data).</li>
 <li class="list-group-item px-0">Iowa <a href="https://www.igsb.uiowa.edu/nrgis/gishome.htm">Natural Resources Geographic Information System (NRGIS)</a></li>
 <li class="list-group-item px-0">NOAA's Ken Waters work with <a href="https://www.weather.gov/regsci/gis/">GIS and NWS warnings</a>
 <div class="small text-muted">They have some historical GIS datasets of warnings too.</div></li>
 <li class="list-group-item px-0"><a href="https://pnwpest.org/US/index.html">Index to Degree-Day Data</a></li>
 <li class="list-group-item px-0"><a href="https://map.nasa.gov/MAP06/">NASA MAP'06 program</a>
  <div class="small text-muted">Has some GIS satellite data.</div></li>
</ul>


</div>
</div>

</div>
<div class="col-lg-6">

<div class="card mb-4">
<div class="card-body">

<div class="d-flex align-items-start gap-3">
    <img src="/images/gisready.png" class="img-fluid flex-shrink-0" alt="GIS ready icon">
    <p class="mb-0">You may have noticed this image appearing on IEM webpages. It signifies that the data link is ready for most GIS systems.</p>
</div>

</div>
</div>


<div class="card mb-4">
<div class="card-body">

<h2 class="h5 card-title">IEM GIS Projects</h2>
<ul class="list-group list-group-flush">
 <li class="list-group-item px-0"><a href="/GIS/tiff/">Grib to GeoTIFF Service</a>
 <div class="small text-muted">Provides various archived grib files in a GeoTIFF format.</div></li>
 <li class="list-group-item px-0"><a href="goes.phtml">GOES Satellite GIS Products</a>
  <div class="small text-muted">Current and archived GIS products from NOAA's GOES satellites.</div></li>
 <li class="list-group-item px-0"><a href="/ogc/">Open GIS Web Services</a>
  <div class="small text-muted">A listing of OGC web services offered by the IEM.</div></li>
 <li class="list-group-item px-0"><a href="/climodat/index.phtml#ks">Iowa Climate Summaries</a>
  <div class="small text-muted">GIS ready data files of monthly and yearly climate summaries dating back to 1951.</div></li>
    <li class="list-group-item px-0"><a href="/GIS/apps/iem/freeze.phtml">IEM Freeze</a>
    <div class="small text-muted">Web mapping application to support winter weather nowcasting.</div></li>
    <li class="list-group-item px-0"><a href="/GIS/radview.phtml">IEM Radview</a>
    <div class="small text-muted">Our effort to provide NEXRAD information in realtime to GIS systems.</div></li>
 <li class="list-group-item px-0"><a href="/rainfall/">IEM Rainfall</a>
  <div class="small text-muted">Gridded rainfall estimates in GIS formats dating back to 2002 for Iowa.</div></li>
 <li class="list-group-item px-0"><a href="/roads/">IEM Iowa Road Conditions</a>
  <div class="small text-muted">Current and archived Iowa road conditions.</div></li>
 <li class="list-group-item px-0"><a href="/cow/">IEM Cow</a>
  <div class="small text-muted">Unofficial NWS polygon warning verification.</div></li>
 <li class="list-group-item px-0"><a href="/docs/nexrad_mosaic/">NEXRAD Mosaic on the IEM</a>
  <div class="small text-muted">Information about the NEXRAD Mosaic that the IEM generates.</div></li>
</ul>


</div>
</div>


<div class="card">
<div class="card-body">

<h2 class="h5 card-title">GIS Shapefiles</h2>
<ul class="list-group list-group-flush">
<li class="list-group-item px-0"><a href="/request/gis/spc_mcd.phtml"><i class="bi bi-download" aria-hidden="true"></i>
SPC Mesoscale Discussion Shapefile Download</a></li>

<li class="list-group-item px-0"><a href="/request/gis/outlooks.phtml"><i class="bi bi-download" aria-hidden="true"></i>
 SPC/WPC Outlook Shapefile Download</a></li>

<li class="list-group-item px-0"><a href="/request/gis/spc_watch.phtml"><i class="bi bi-download" aria-hidden="true"></i>
 SPC Watch Polygon Shapefile Download</a></li>

<li class="list-group-item px-0">Past 24 hours of Storm Reports
 <div><a href="/data/gis/shape/4326/us/lsr_24hour.zip">ESRI Shapefile</a>,
 <a href="/data/gis/shape/4326/us/lsr_24hour.csv">Comma Delimited</a>,
 <a href="/data/gis/shape/4326/us/lsr_24hour.geojson">GeoJSON</a></div>
 <div class="small text-muted">The IEM parses the realtime feed of NWS Local Storm Reports. Every
 5 minutes, a process collects up the last 24 hours worth of reports and
 dumps them to the above files.</div></li>

 <li class="list-group-item px-0"><a href="/request/gis/lsrs.phtml">Archived Local Storm Reports</a>
 <div class="small text-muted">Generate a shapefile of LSRs for a period of your choice dating back
  to 2003.</div></li>
 <li class="list-group-item px-0"><a href="/data/gis/shape/4326/us/current_ww.zip">Current NWS Warnings</a>
 <div class="small text-muted">A shapefile of active county based and polygon based weather warnings.
This file is updated every minute.</div></li>
 <li class="list-group-item px-0"><a href="/request/gis/watchwarn.phtml">Archived NWS Warnings</a>
 <div class="small text-muted">Generate a shapefile of weather warnings for a time period of your
 choice.</div></li>

 <li class="list-group-item px-0"><a href="/data/gis/shape/4326/us/current_nexattr.zip">Current NEXRAD Storm Attributes</a>
  <div class="small text-muted">Point shapefile generated every minute containing a summary of
   NEXRAD storm attributes.</div></li>
 <li class="list-group-item px-0"><a href="/request/gis/nexrad_storm_attrs.php">Archived NEXRAD Storm Attributes</a>
 <div class="small text-muted">Generate a shapefile of storm attributes for a RADAR and time period
 of your choice from the archive.</div></li>
 <li class="list-group-item px-0"><a href="/data/gis/shape/4326/iem/coopobs.zip">NWS COOP Observations</a>
   <div class="small text-muted">Today's climate reports.</div></li>
 <li class="list-group-item px-0"><a href="/request/gis/sps.phtml">Special Weather Statement (SPS) Polygons</a>
 <div class="small text-muted">Shapefile download of SPS polygons and IBW tags.</div></li>
 <li class="list-group-item px-0"><a href="/data/gis/">Browse</a> GIS data stored on the IEM website.</li>

<li class="list-group-item px-0"><a href="/request/gis/wpc_mpd.phtml"><i class="bi bi-download" aria-hidden="true"></i>
WPC Precip Discussion MPD Polygon Shapefile Download</a></li>

</ul>

</div>
</div>

</div></div>
EOM;
$t->render("single.phtml");
