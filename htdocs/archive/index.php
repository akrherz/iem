<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/generators.php";

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

<h3>Multi-RADAR Multi-Sensor (MRMS) Archiving</h3>

<p>The IEM maintains some unique archiving of the 
<a href="https://www.nssl.noaa.gov/projects/mrms/">MRMS Project</a>.
The archive beginning date and variable coverage varies with the links below.
There is
a helpful <a href="https://www.nssl.noaa.gov/projects/mrms/operational/tables.php">Grib Table</a> and
you should use the <a href="https://mrms.ncep.noaa.gov/data/">MRMS Data Website</a>
for realtime data.</p>

<ul>
  <li><a href="https://drive.google.com/drive/folders/1JCajASK61bFp9h3khOb9PjoS04Um0DfQ?usp=sharing">~Complete Hourly Zipfiles on Google Drive</a> since 28 Sep 2019.
  <br />These are based on whatever was provided by the LDM NCEP feed and
  there is no mechanism attempted to repair any holes (quasi rare) from the
  LDM feed.  Automated downloads from the Google Drive are difficult, but is
  your only option if the next link below does not have your files of interest.</li>

  <li><a href="https://mrms.agron.iastate.edu">Local Cache of ~Complete Hourly Zip Files</a>
  <br />Same files as found on the Google Drive, but served from a local
  spinning disk and so is <strong>easy to script against</strong> to download
  a large chunk of data.  The intention is to keep about the last year's worth
  of data available here.</li>

  <li><a href="https://mtarchive.geol.iastate.edu/${d}/mrms/ncep/">Mtarchive Daily Selected Files</a> contains
  selected grib2 files of interest and has a more aggressive process that attempts to fill
  in holes based on NCEP LDM or HTTP outages.  This archive goes back to the beginning
  of MRMS, but the number of data types archived varies.</li>

  <li><a href="http://metfs1.agron.iastate.edu/data/mrms/">Current MRMS Files</a>
  <br /> provides
  files in a staging area before they are zipped up and uploaded to CyBox at
  the link above.  This link does not provide anything more than the
  <a href="https://mrms.ncep.noaa.gov/data/">MRMS Data Website</a> does.</li>
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

<li><a href="https://s3.amazonaws.com/noaa-nexrad-level2/index.html">Amazon S3 NEXRAD II Archive</a>
<br />Your first stop if you are looking for archived Level II files!</li>

<li><a href="/archive/nexrad/">NIDS NEXRAD Data</a>
 <br>NEXRAD data from the seven sites (DMX,DVN,OAX,FSD,ARX,MPX,EAX) with
Iowa coverage.  Since mid April 2002, all NIDS products are archived. Before
then, only base reflectivity was saved.</li>

<li><a href="https://mesonet-nexrad.agron.iastate.edu/level2/raw/">IEM 2 day Level II Archive</a>
 <br />The IEM maintains an archive of Level II data for roughly the past two days.</li>

<li><a href="http://hurricane.ncdc.noaa.gov/pls/plhas/has.dsselect">NCDC ~Complete NEXRAD archive</a>
 <br />This is the one-stop place for historical Level II and Level III NEXRAD information.  A wonderful site!</li>

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
<p>See this <a href="/onsite/news.phtml?id=1408">news item</a> for more details
on this archive and how it is made available.</p>
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

</div><div class="col-md-6 col-sm-6">
		
<h3>Raw Data</h3>
<ul>
 <li>BUFKIT archives
  <br /><a href="/archive/data/">Iowa Only</a> The general IEM data archive
  contains a sub-directory called 'bufkit'.
   This directory contains model point soundings for locations near Iowa. The
   archive started 25 January 2006 - 27 March 2015.
  <br /><a href="https://mtarchive.geol.iastate.edu/">Mtarchive BUFKIT Archive</a>
  This archive contains data for many more sites and models.
  <br /><a href="/api/1/docs#/default/service_nws_bufkit__fmt__get">IEM API BUFKIT Webservice</a>
  allows for nearest in space/time searches, atomic data download and more.
  </li>

 <li><a href="https://mtarchive.geol.iastate.edu/">GEMPAK data archive</a>
  <br />Archive of gempak products taken from the UNIDATA NOAAPORT feed.  This
   archive dates back to 2001 and for some dates even further.</li>

 <li><a href="http://home.chpc.utah.edu/~u0553130/Brian_Blaylock/hrrr_FAQ.html">HRRR Model Archive</a>
 <br />Archive maintained by University of Utah of the HRRR model.</li>
   
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

<li><a href="https://www.weather.gov/unr/uac">Precipitable Water Climatologies</a>
 <br />Fascinating month-by-month plots of PWAT climatologies for the RAOB sites in the CONUS</li>

<li><a href="http://www2.mmm.ucar.edu/imagearchive/">UCAR plot archive</a>
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
 <li><a href="https://www.wpc.ncep.noaa.gov/dailywxmap/pdffiles.html">Recent maps from NCEP</a></li>
 <li><a href="https://www.wpc.ncep.noaa.gov/dailywxmap/index.html">Daily maps</a></li>
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
