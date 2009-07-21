<?php 
include("../../config/settings.inc.php");
$THISPAGE = "archive-main";
$TITLE = "IEM | Archived Data Resources";
include("$rootpath/include/header.php"); ?>

<div style="width:800px;">

<h3 class="heading">Archived Data & Plots</h3>

<p class="story">This page contains a listing of archive resources.  A brief
description of each link is included to aid your search.  If you are still
having difficulty finding something, please let us know. </p>

<div style="width:390px; float:left;">

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

<h3>RADAR Data</h3>
<ul>

<li><a href="<?php echo $rooturl; ?>/archive/nexrad/">NIDS NEXRAD Data</a>
 <br>NEXRAD data from the seven sites (DMX,DVN,OAX,FSD,ARX,MPX,EAX) with
Iowa coverage.  Since mid April 2002, all NIDS products are archived. Before
then, only base reflectivity was saved.</li>

<li><a href="http://mesonet.agron.iastate.edu/data/nexrd2/raw/">IEM 2 day Level II Archive</a>
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
</ul>
</div>
<div style="width:390px; float:right;">

<h3>Raw Data</h3>
<ul>
 <li><a href="/archive/data/">Bufkit archive</a>
  <br />The general IEM data archive contains a sub-directory called 'bufkit'.
   This directory contains model point soundings for locations near Iowa. The
   archive started 25 January 2006.</li>

 <li><a href="http://mtarchive.geol.iastate.edu/">GEMPAK data archive</a>
  <br />Archive of gempak products taken from the UNIDATA NOAAPORT feed.  This
   archive dates back to 2001 and for some dates even further.</li>

 <li><a href="<?php echo $rooturl; ?>/archive/raw/">IEM Network Data</a>
  <br />IEM data in its original unprocessed form.  ASOS/AWOS METAR observation,
   RWIS comma-deliminated data, schoolnet csv data, SCAN site format and COOP
   observations</li>

 <li><a href="/archive/rer/">NWS Record Event Reports</a>
  <br />Daily reports of record temperatures and precipitation for 
   Iowa since November 2001</li>

 <li><a href="http://lead.unidata.ucar.edu:8080/thredds/catalog.html">Unidata IDD 6 month archive</a>
  <br />Archive of raw data provided by Unidata for the past 6 months!</li>
 <li><a href="http://nomads.ncdc.noaa.gov/data/">NCDC NOMADS Big Archive!!</a>
  <br />Lots of raw model data and other goodies, a definite must-visit.</li>

</ul>

<h3>Misc</h3>
<ul>
<li><a href="<?php echo $rooturl; ?>/browser/">Archived Data Browser</a>
  <br />Browse the archive of products via this frames based interface.</li> 

<li><a href="http://archive.atmos.colostate.edu/">NWS DIFAX Archive (2000-)</a>
 <br />Excellent archive of the NWS DIFAX products.</li>

<li><a href="http://www.crh.noaa.gov/unr/?n=pw">Precipitable Water Climatologies</a>
 <br />Fascinating month-by-month plots of PWAT climatologies for the RAOB sites in the CONUS</li>

<li><a href="http://locust.mmm.ucar.edu/case-selection/">UCAR plot archive</a>
  <br />Assorted RADAR, satellite, and model plots back to 1998.</li>

<li><a href="<?php echo $rooturl; ?>/archive/data/">IEM Generated Plots</a>
  <br>Images and data products mostly displayed in real time on the current
data page.  Iowa Mesonet plots, hourly precip plots, mesonet stats and 
COOP precip plots are examples.</li>

<li><a href="<?php echo $rooturl; ?>/archive/gempak/">IEM Data in GEMPAK Format</a>
  <br />IEM surface data in GEMPAK format.  Data files exist with different
combinations of IEM networks.</li>

<li><a href="http://www.mdl.nws.noaa.gov/~mos/archives/">Model MOS Archive</a>
<br>NWS archive of model output statistics (MOS)</li>

<li><a href="http://www.pals.iastate.edu/archivewx/data/">PALS WX Image Archive</a><br />The PALS website generates hourly plots of US weather.  Of interest are
archives of RUC, ETA, and AVN model plots.  National radar summaries, 
surface plots and other plots.</li>

<li><a href="ftp://ftp.wcc.nrcs.usda.gov/support/climate/wind_daily">NRCS wind climatologies (1961-1990)</a></li>
<li><a href="http://climate.engin.umich.edu/tornadopaths/">Historical Tornado Tracks</a></li>
</ul>

<h3>US Daily Weather Maps</h3>
<ul>
 <li><a href="http://www.hpc.ncep.noaa.gov/dailywxmap/pdffiles.html">Recent maps from NCEP</a></li>
 <li><a href="http://www.hpc.ncep.noaa.gov/dailywxmap/index.html">Daily maps</a></li>
 <li><a href="http://docs.lib.noaa.gov/rescue/dwm/data_rescue_daily_weather_maps.html">Maps from 1872 to 2002</a></li>
 <li><a href="http://www7.ncdc.noaa.gov/IPS/">NCDC Image and Publications System</a></li>
</ul>

<h3>Data download forms</h3>
<ul>
<li><a href="<?php echo $rooturl; ?>/request/awos/1min.php">1 minute AWOS data</a>
 <br>Download/Plot/View 1 minute AWOS data since 1 Jan 1995.</li>

<li><a href="<?php echo $rooturl; ?>/schoolnet/dl/">1 minute schoolNet data</a><br>Download/View 1 minute schoolNet data since 12 Feb 2002.</li>

<li><a href="<?php echo $rooturl; ?>/cgi-bin/precip/catAZOS.py">Hourly ASOS/AWOS Precip Reports</a>
 <br>Hourly precipitation HTML grids from the archive.  A useful tool to 
quickly find precipitation totals.</li>

<li><a href="<?php echo $rooturl; ?>/request/download.phtml">Hourly ASOS/AWOS/RWIS Observations</a>
<br />Quickly query the IEM databases for historical RWIS/ASOS/AWOS observations.
This dataset contains the raw observations.</li>

</ul>
</div>

<p style="clear: both;">Are we forgetting something?  Please let us know of other
archives that are available for Iowa data.</p>
</div>

<?php include("$rootpath/include/footer.php"); ?>
