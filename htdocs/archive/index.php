<?php 
include("../../config/settings.inc.php");
include("../../include/myview.php");
include("../../include/generators.php");

define("IEM_APPID", 19);
$t = new MyView();
$t->thispage = "archive-main";
$t->title = "Archived Data Resources";

$dllist = get_iemapps_tags("download");
$d = date("Y/m/d");
$t->content = <<<EOF
<h3>Archived Data & Plots</h3>

<p>This page contains a listing of archive resources.  A brief
description of each link is included to aid your search.  If you are still
having difficulty finding something, please let us know. </p>

<div class="row"><div class="col-md-6 col-sm-6">
		
<h3>Storm Event Pictures</h3>
<ul>
 <li><a href="/cases/060413/">13 April 2006</a>
  <br />Iowa City tornado.</li>
 <li><a href="/cases/051112/">12 November 2005</a>
  <br />Tornadoes of Woodward, Stratford, and Ames.</li>
 <li><a href="/cases/080525/">25 May 2008</a>
  <br />Parkersburg EF5 Tornado.</li>
 <li><a href="/cases/">... View all ...</a></li>
</ul>

<h3>NWS Watch/Warnings/Advisories</h3>
<ul>
 <li><a href="/request/gis/watchwarn.phtml">Download Shapefiles</a>
  <br />Download shapefiles of warning geometries and metadata.</li>
 <li><a href="/vtec/search.php">Search by County/Zone</a>
  <br />Find archived warnings by searching for a county or zone.</li>
 <li><a href="/vtec/">VTEC Browser</a>
  <br />Interactively navigate our archive of warnings.</li>
</ul>

<h3>RADAR Data</h3>
<ul>

<li><a href="/archive/nexrad/">NIDS NEXRAD Data</a>
 <br>NEXRAD data from the seven sites (DMX,DVN,OAX,FSD,ARX,MPX,EAX) with
Iowa coverage.  Since mid April 2002, all NIDS products are archived. Before
then, only base reflectivity was saved.</li>

<li><a href="http://mesonet-nexrad.agron.iastate.edu/level2/raw/">IEM 2 day Level II Archive</a>
 <br />The IEM maintains an archive of Level II data for roughly the past two days.</li>

<li><a href="http://hurricane.ncdc.noaa.gov/pls/plhas/has.dsselect">NCDC ~Complete NEXRAD archive</a>
 <br />This is the one-stop place for historical Level II and Level III NEXRAD information.  A wonderful site!</li>

<li><a href="http://mesonet.tamu.edu/products/RADAR/nexrad/CRAFT/">Texas Mesonet LEVEL II archive</a>
 <br />Past 30 days of Level II data for all NEXRAD sites.</li>

<li><a href="http://mesonet.tamu.edu/products/RADAR/nexrad/NIDS/">Texas Mesonet LEVEL III archive</a>
<br />Past 30 days of Level III data for all NEXRAD sites.</li>

 <li><a href="/archive/data/">GIS NEXRAD Composites</a>
  <br />Composites of NEXRAD base reflectivity.  The raw files are found
   in the general IEM archive in the sub-directory called 'GIS/uscomp/'.</li>

<li><a href="http://vortex.plymouth.edu/nids.html">Single Site NIDS Imagery</a>
 <br />You can generate images from their online archive!</li>
</ul>

<h3>Satellite</h3>
<ul>
 <li><a href="http://www.class.noaa.gov/">NOAA Satellite and Information Service</a>
 <br />A wonderful site to download historical satellite data.</li>
 <li><a href="http://stormtrack.nssl.noaa.gov/">NSSL Storm Tracker</a>
 <br />Current and archived satellite imagery along with some derived products.</li>
</ul>


<h3>NWS Text Products</h3>
<br />The IEM archives all NWS issued text products.  Unfortunately, the we 
don't have this full archive online yet.  NCDC has a <a href="http://has.ncdc.noaa.gov/pls/plhas/HAS.FileAppSelect?datasetname=9957ANX">big archive</a> of
this data back to 2001.  The IEM's archives can be found:
<ul>
 <li><a href="/wx/afos/">AFOS Product Finder</a>
  <br />If you know what you are looking for, this app works great!</li>
 <li><a href="/archive/data/{$d}/text/noaaport/">Simple directory listing</a>
  <br />Certain warning type products can be found in the main IEM data archive
  directory structure.</li>
 <li><a href="/wx/afos/list.phtml">List Products by WFO by Date</a>
  <br />View quick listings of issued products by forecast office and by date.</li>
  <li><a href="/archive/rer/">NWS Record Event Reports</a>
  <br />Daily reports of record temperatures and precipitation for
   Iowa since November 2001</li>
</ul>
		
</div><div class="col-md-6 col-sm-6">
		
<h3>Raw Data</h3>
<ul>
 <li><a href="/archive/data/">Bufkit archive</a>
  <br />The general IEM data archive contains a sub-directory called 'bufkit'.
   This directory contains model point soundings for locations near Iowa. The
   archive started 25 January 2006.</li>

 <li><a href="http://mtarchive.geol.iastate.edu/">GEMPAK data archive</a>
  <br />Archive of gempak products taken from the UNIDATA NOAAPORT feed.  This
   archive dates back to 2001 and for some dates even further.</li>

 <li><a href="/archive/raw/">IEM Network Data</a>
  <br />IEM data in its original unprocessed form.  ASOS/AWOS METAR observation,
   RWIS comma-deliminated data, schoolnet csv data, SCAN site format and COOP
   observations</li>


 <li><a href="http://lead.unidata.ucar.edu:8080/thredds/catalog.html">Unidata IDD 6 month archive</a>
  <br />Archive of raw data provided by Unidata for the past 6 months!</li>
 <li><a href="http://nomads.ncdc.noaa.gov/data/">NCDC NOMADS Big Archive!!</a>
  <br />Lots of raw model data and other goodies, a definite must-visit.</li>

</ul>

<h3>Misc</h3>
<ul>
<li><a href="/timemachine/">Archived IEM Product Browser</a>
  <br />This "time machine" interface allows for quick browsing of IEM Products.</li> 

<li><a href="http://archive.atmos.colostate.edu/">NWS DIFAX Archive (2000-)</a>
 <br />Excellent archive of the NWS DIFAX products.</li>

<li><a href="http://www.crh.noaa.gov/unr/?n=pw">Precipitable Water Climatologies</a>
 <br />Fascinating month-by-month plots of PWAT climatologies for the RAOB sites in the CONUS</li>

<li><a href="http://locust.mmm.ucar.edu/case-selection/">UCAR plot archive</a>
  <br />Assorted RADAR, satellite, and model plots back to 1998.</li>

<li><a href="/archive/data/">IEM Generated Plots</a>
  <br>Images and data products mostly displayed in real time on the current
data page.  Iowa Mesonet plots, hourly precip plots, mesonet stats and 
COOP precip plots are examples.</li>

<li><a href="/archive/gempak/">IEM Data in GEMPAK Format</a>
  <br />IEM surface data in GEMPAK format.  Data files exist with different
combinations of IEM networks.</li>

<li><a href="http://www.mdl.nws.noaa.gov/~mos/archives/">Model MOS Archive</a>
<br>NWS archive of model output statistics (MOS)</li>

<li><a href="/mos/">IEM's Model MOS Archive</a>
<br>IEM's archive of model output statistics (MOS)</li>

<li><a href="http://www.ncdc.noaa.gov/swdi">NCDC Severe Weather Data Inventory</a>
<br />Extremely fancy archive of various datasets dealing with severe
weather.</li>

<li><a href="http://www.ncdc.noaa.gov/ussc/USSCAppController?action=map">NCDC Snow Climatologies</a>
<br />Lots of great statistics on snowfall and snow depth.</li>

<li><a href="http://www.pals.iastate.edu/archivewx/data/">PALS WX Image Archive</a><br />The PALS website generates hourly plots of US weather.  Of interest are
archives of RUC, ETA, and AVN model plots.  National radar summaries, 
surface plots and other plots.</li>

<li><a href="ftp://ftp.wcc.nrcs.usda.gov/support/climate/wind_daily">NRCS wind climatologies (1961-1990)</a></li>

<li><a href="http://climate.engin.umich.edu/tornadopaths/">Historical Tornado Tracks</a></li>

<li><a href="http://ida.water.usgs.gov/ida/">USGS Instantaneous Data Archive</a>
<br />Goldmine of historical USGS river gage data.</li>
</ul>

<h3>US Daily Weather Maps</h3>
<ul>
 <li><a href="http://www.hpc.ncep.noaa.gov/dailywxmap/pdffiles.html">Recent maps from NCEP</a></li>
 <li><a href="http://www.hpc.ncep.noaa.gov/dailywxmap/index.html">Daily maps</a></li>
 <li><a href="http://docs.lib.noaa.gov/rescue/dwm/data_rescue_daily_weather_maps.html">Maps from 1872 to 2002</a></li>
 <li><a href="http://www7.ncdc.noaa.gov/IPS/">NCDC Image and Publications System</a></li>
</ul>

<h3>Data download forms</h3>
{$dllist}
</div></div>

<p style="clear: both;">Are we forgetting something?  Please let us know of other
archives that are available for Iowa data.</p>
EOF;
$t->render('single.phtml');
?>