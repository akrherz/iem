<?php 
include("../../config/settings.inc.php");
$page = "archive";
$TITLE = "IEM | Archived Data Resources";
include("$rootpath/include/header.php"); ?>

<TR><TD>

<h3 class="heading">Archived Data & Plots</h3>

<div class="text">
<p class="story">This page contains a listing of archive resources.  A brief
description of each link is included to aid your search.  If you are still
having difficulty finding something, please let us know.</p>

<h3>RADAR Data</h3>
<ul>

<li><a href="<?php echo $rooturl; ?>/archive/nexrad/">NIDS NEXRAD Data</a><br>
<dd>NEXRAD data from the seven sites (DMX,DVN,OAX,FSD,ARX,MPX,EAX) with
Iowa coverage.  Since mid April 2002, all NIDS products are archived. Before
then, only base reflectivity was saved.</dd></li>

<li><a href="http://hurricane.ncdc.noaa.gov/pls/plhas/has.dsselect">NCDC ~Complete NEXRAD archive</a><br />
<dd>This is the one-stop place for historical Level II and Level III NEXRAD information.  A wonderful site!</dd></li>

<li><a href="http://mesonet.tamu.edu/products/RADAR/nexrad/CRAFT/">Texas Mesonet LEVEL II archive</a><br />
<dd>Past 30 days of Level II data for all NEXRAD sites.</dd></li>

<li><a href="http://mesonet.tamu.edu/products/RADAR/nexrad/NIDS/">Texas Mesonet LEVEL III archive</a><br />
<dd>Past 30 days of Level III data for all NEXRAD sites.</dd></li>

</ul>


<h3>Misc</h3>
<ul>
<li><a href="<?php echo $rooturl; ?>/browser/">Archived Data Browser</a><br>
<dd>Browse the archive of products via this frames based interface.</dd> 

<li><a href="<?php echo $rooturl; ?>/archive/data/">IEM Generated Plots</a><br>
<dd>Images and data products mostly displayed in real time on the current
data page.  Iowa Mesonet plots, hourly precip plots, mesonet stats and 
COOP precip plots are examples.</dd>

<li><a href="http://mtarchive.geol.iastate.edu/">GEMPAK data archive</a><br>
<dd>Archive of gempak products taken from the UNIDATA NOAAPORT feed.  This
archive dates back to 2001 and for some dates even further.</dd></li>

<li><a href="<?php echo $rooturl; ?>/archive/gempak/">IEM Data in GEMPAK Format</a><br>
<dd>IEM surface data in GEMPAK format.  Data files exist with different
combinations of IEM networks.</dd>

<li><a href="http://www.mdl.nws.noaa.gov/~mos/archives/">Model MOS Archive</a>
<br><dd>NWS archive of model output statistics (MOS)</dd>

<li><a href="<?php echo $rooturl; ?>/archive/rer/">NWS Record Event Reports</a><br />
 <dd>An archive of Record Event Reports sent out for locations in Iowa dating
back to November 2001.  These are the reports of record rainfall, snowfall,
and high/low temperature.  This archive is thought to be complete.</dd>


<li><a href="<?php echo $rooturl; ?>/archive/raw/">RAW IEM Data</a><br>
<dd>IEM data in its original unprocessed form.  ASOS/AWOS METAR observation,
RWIS comma-deliminated data, schoolnet csv data, SCAN site format and COOP
observations</dd>

<!--
<li><a href="http://www.pals.iastate.edu/archivewx/data/">PALS WX Image Archive</a><br>
<dd>The PALS website generates hourly plots of US weather.  Of interest are
archives of RUC, ETA, and AVN model plots.  National radar summaries, 
surface plots and other plots make up the archive that dates back to ~1998.</dd>
-->

<li><a href="<?php echo $rooturl; ?>/request/awos/1min.php">1 minute AWOS data</a><br>
<dd>Download/Plot/View 1 minute AWOS data since 1 Jan 1995.</dd>

<li><a href="<?php echo $rooturl; ?>/schoolnet/dl/">1 minute schoolNet data</a><br>
<dd>Download/View 1 minute schoolNet data since 12 Feb 2002.</dd>

<li><a href="<?php echo $rooturl; ?>/cgi-bin/precip/catAZOS.py">Hourly ASOS/AWOS Precip Reports</a><br>
<dd>Hourly precipitation HTML grids from the archive.  A useful tool to 
quickly find precipitation totals.</dd>

<li><a href="<?php echo $rooturl; ?>/request/download.phtml">Hourly ASOS/AWOS/RWIS Observations</a>
<dd>Quickly query the IEM databases for historical RWIS/ASOS/AWOS observations.
This dataset contains the raw observations.</dd>

</ul>

<p class="story">Are we forgetting something?  Please let us know of other
archives that are available for Iowa data.</p></div>

<?php include("$rootpath/include/footer.php"); ?>
