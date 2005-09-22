<?php 
  $TITLE = "IEM | AWOS Network";
include("/mesonet/php/include/header2.php"); 
?>

<h3 class="heading">AWOS Network</h3><p>

<div class="text">
Automated Weather Observing System (AWOS) stations are often
grouped together with the ASOS stations, but they are not the same.  Like the
ASOS, the AWOS sensors primarily provide the aviation community with current
weather observations.  The data is also transmitted by phone lines or satellite
uplinks for use by other agencies. The AWOS sites are either 
federally operated by the FAA or 
some of them are locally maintained by state agencies.[1]</p> 
<br><br>

<div id="iem-image"><img
src="http://www.meteor.iastate.edu/gccourse/evals/page1.jpg"></div>

<table width="100%">
<tr><td width="50%" valign="TOP">

<h3 class="subtitle">Docs:</h3>
<ul>
<li><b>27 Oct 2004:</b> <a href="http://mesonet.agron.iastate.edu/onsite/news.phtml?id=300">About AWOS 80+ Dewpoints</a></li>
<li><b>25 Jan 2004:</b> <a href="reports/awos040125.pdf">AWOS 'calibration' issues</a></li>
<li><a href="manual/">ADAS/AWOS Manual</a></li>
<li><a href="skyc.phtml">Note about archived cloud coverages</a></li>
</ul>

<h3 class="subtitle">Current AWOS Data:</h3>
<UL>
 <li><a href="current.phtml">Sortable Current Conditions</a></li>
 <li><a href="/data/mesonet.gif">Combined Mesonet</a></li>
 <li><a href="/data/awos.gif">AWOS Mesonet</a></li>
 <li><a href="/data/heat.gif">Heat Index</a></li>
 <li><a href="/data/wcht.gif">Wind Chill Index</a></li>
 <li><a href="/data/relh.gif">Relative Humidity</a></li>
 <li><a href="/data/awos_rtp.shef">12Z RTP First Guess</a></li>
</UL>

<p><h3 class="subtitle">Historical Data:</h3>

Observations from the AWOS network are saved in 1 minute intervals.  The DOT
provides the IEM with a monthly update of this 1 minute dataset.  The 1 minute
data from the previous month is uploaded to the IEM server around the first 
week of the month.

<ul>
<li><a href="/plotting/awos/1station_1min.php">Daily Data Plotting</a></li>
<li><a href="/request/awos/1min.php">Download/View/Plot Archived Data</a></li>
<li><a href="/AWOS/reports/2002precip.phtml">2002 Precipitation Totals</a></li>
<li><a href="/AWOS/reports/2003precip.phtml">2003 Precipitation Totals</a></li>
<li><a href="/AWOS/reports/2004precip.phtml">2004 Precipitation Totals</a></li>
<li><a href="/cgi-bin/precip/catAZOS.py">Hourly Precipitation</a> tables</li>
</ul>

</td><td valign="top" width="50%"> 

<h3 class="subtitle">MADIS QC Mesages:</h3>
<ul>
 <li><a href="/QC/madis/network.phtml?network=AWOS">Raw QC Values</a></li>
 <li><a href="http://www-sdd.fsl.noaa.gov/MSAS/qcms_data/qc4/qchour.txt">Hourly</a></li>
 <li><a href="http://www-sdd.fsl.noaa.gov/MSAS/qcms_data/qc4/qcday.txt">Daily</a></li>
 <li><a href="http://www-sdd.fsl.noaa.gov/MSAS/qcms_data/qc4/qcweek.txt">Weekly</a></li>
 <li><a href="http://www-sdd.fsl.noaa.gov/MSAS/qcms_data/qc4/qcmonth.txt">Monthly</a></li>
</ul>

<h3 class="subtitle">Comparisons:</h3>
<ul>
  <li><a href="/wx/data/models/ruc2_iem_T.gif">Temperatures vs RUC2 Model</a></li>
  <li><a href="/data/temps.gif">Temperatures vs RWIS Network</a></li>
  <li><a href="/data/snet/Tcompare.gif">Temperatures vs SchoolNet Network</a></li>
  <li><a href="/wx/data/models/ruc2_iem_Td.gif">Dew Points vs RUC2 Model</a></li>
  <li><a href="/data/dewps.gif">Dew Points vs RWIS Network</a></li>
  <li><a href="/data/snet/Dcompare.gif">Dew Points vs SchoolNet Network</a></li>
  <li><a href="/wx/data/models/ruc2_iem_V.gif">Winds vs RUC2 Model</a></li>
  <li><a href="/data/winds.gif">Winds vs RWIS Network</a></li>
  <li><a href="/wx/data/models/ruc2_iem_Rh.gif">Relative Humidity vs RUC2 Model</a></li>
  <li><a href="/data/snet/Pcompare.gif">Pressure vs SchoolNet Network (mb)</a></li>
  <li><a href="/data/snet/P2compare.gif">Pressure vs SchoolNet Network (in)</a></li>
</ul>


<h3 class="subtitle">QC Info:</h3>
<ul>
<li>Sites <a href="/QC/offline.php">offline</a> [<a href="http://db1.mesonet.agron.iastate.edu/GIS/apps/stations/offline.php?network=awos">Graphical View</a>]</li>
<li><a href="http://mesonet.agron.iastate.edu/QC/tickets.phtml">Open Trouble Tickets</a></li>
<li><a href="http://mesonet.agron.iastate.edu/AWOS/reports/qcal.phtml">Questionable Calibration Events</a></li>
</ul>

<h3 class="subtitle">Hourly Mesonet + NEXRAD:</h3>
<UL>
	<li><a href="../data/DMX_radar.gif">Des Moines</a></li>
        <li><a href="../data/OAX_radar.gif">Omaha</a></li>
        <li><a href="../data/DVN_radar.gif">Davenport</a></li>
	<li><a href="../data/FSD_radar.gif">Sioux Falls</a></li>
        <li><a href="../data/ARX_radar.gif">LaCrosse</a></li>
</UL>

</td></tr></table>

<b>References:</b><br>
<b>1</b> <a href="http://www.faa.gov/asos/whatawos.htm">http://www.faa.gov/asos/whatawos.htm</a>
 , viewed: 21 Feb 2002

<br><br></div>

<?php include("/mesonet/php/include/footer.php"); ?>
