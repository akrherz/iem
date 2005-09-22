<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<HEAD>
	<TITLE>IEM | Current Data</TITLE>
	<META NAME="AUTHOR" CONTENT="Daryl Herzmann">
	<link rel="stylesheet" type="text/css" href="/css/mesonet.css">
</HEAD>

<?php 
	$page = "current";
	include("../include/header2.php"); 
?>

<div class="ptitle">Current Data</div>

<table>
<tr><td>

<!-- Station Plots -->
<table bgcolor="#778899" border=0 cellspacing=0 cellpadding=2>
<tr bgcolor="#778899">
  <td colspan=2 style="border:ridge 2pt;
  padding:0in 5pt 0in 5pt"><font color="#ffff00"><b>Current Station Plots</b></font></td>
  </tr>

<tr bgcolor="#ffffff">
  <td><i>Observing Network:</i></td>
  <td><i>Last Update, # Reporting</i></td>
  </tr>

<tr bgcolor="#ffffff">
  <td><a href="/data/asos.gif">ASOS + AWOS</a>
     <br>Iowa Airport Stations</td>
  <td> <?php include("../data/asos.stat");  ?> Reporting </td>
  </tr>
<tr bgcolor="#ffffe0">
  <td><a href="/data/awos.gif">AWOS</a>
     <br>Iowa DOT Airport Stations</td>
  <td> <?php include("../data/awos.stat");  ?> Reporting </td>
  </tr>
<tr bgcolor="#ffffff">
  <td><a href="/data/rwis.gif">RWIS</a>
    <br>Roadway Weather Stations</td>
  <td> <?php include("../data/rwis.stat");  ?> Reporting </td>
  </tr>
<tr bgcolor="#ffffe0">
  <td><a href="/data/snet/mesonet.gif">SchoolNet</a> 
    <br>(KCCI-TV + KELO-TV)</td>
  <td> <?php include("../data/snet.stat");  ?> Reporting </td>
  </tr>
</table>
<!-- End Station Plots -->

</td><td>

<table bgcolor="#778899" border=0 cellspacing=0 cellpadding=2>
<tr bgcolor="#778899">
  <td colspan=2 style="border:ridge 2pt;
  padding:0in 5pt 0in 5pt"><font color="#ffff00"><b>Current Data Plots</b></font></td>
  </tr>

<tr bgcolor="#ffffff">
  <td><i>Product:</i></td>
  <td><i>From Network:</i></td>
  </tr>

<tr bgcolor="#ffffff">
  <td><a href="/data/1hprecip.gif">Last Hour's Rainfall</a>
    <br></td>
  <td>ASOS + AWOS</td>
  </tr>



</table>

</td></tr>
</table>

<p>
<TABLE class="page" style="padding: 2;">
<TR>
        <TD colspan="2"><font class="bluet"><B>Current Data:</B></font></TD>
        <TH>
        <?php include("../data/mesoTime.txt");  ?>
        </TH>
</TR>

<TR bgcolor="#EEEEEE">
        <TD rowspan="15" bgcolor="white"><BR></TD>
        <TD>Combined Mesonet.</TD>
        <TD>[ <a href="/data/mesonet.gif">Iowa</a> ] &nbsp; 
	  [ <a href="/data/MWmesonet.gif">Upper Mid-West</a> ] &nbsp;
	  [ <a href="/data/iem_gray.gif">Large Font</a> ] <br>
	  [ <a href="/data/CBF_mesonet.gif">Council Bluffs</a> ] &nbsp;
	  [ <a href="/data/CID_mesonet.gif">Cedar Rapids</a> ] &nbsp;
	  [ <a href="/data/DSM_mesonet.gif">Des Moines</a> ]
	</TD>
</TR>

<TR>
	<TD>Precipitation [ASOS/AWOS]</TD>
	<TD> <a href="/data/1hprecip.gif">Last Hour</a> &nbsp; | &nbsp;
	<a href="/data/summary/today_prec.gif">Today</a>
	</TD>
</TR>

<TR bgcolor="#EEEEEE">
	<TD>Precipitation [NEXRAD]</TD>
	<TD> <a href="/data/nexradPrecip1h.gif">1 hour Estimate</a>
	</TD>
</TR>

<TR>
        <TD>20min Mesonet + DMX NEXRAD</TD>
        <TD> <a href="../data/20radarOverlay_0.gif">Image</a> &nbsp; | &nbsp;
        <a href="../data/20radarLoop.html">Loop</a> &nbsp; | &nbsp;
        <a href="../data/20radarLoop_s.html">Small Loop</a>
        </TD>
</TR>

<TR bgcolor="#EEEEEE">
        <TD>20min Mesonet + Composite NEXRAD</TD>
        <TD> <a href="../data/MWoverlay_0.gif">Image</a> &nbsp; | &nbsp;
        <a href="../data/MWoverlayLoop.html">Loop</a> 
        </TD>
</TR>



<TR>
	<TD>Satellite</TD>
	<TD><a href="http://www.meteor.iastate.edu/wx/data/current/IAsatvis.gif">Visible</a> &nbsp; | &nbsp;
	<a href="http://www.meteor.iastate.edu/wx/data/current/IAsatir.gif">Infared</a> &nbsp; | &nbsp;
  <a href="/wx/data/mesoVis.gif">Visible with Mesonet</a>
	</TD>
</TR>
<TR bgcolor="#EEEEEE">
        <TD>Visibility</TD>
	<TD><a href="/data/vsby.gif">Plot</a></TD>
</TR>


<TR>
        <TD>Wind Chill Index. [ASOS/RWIS]</TD>
        <TD> <a href="/data/wcht.gif">Plot</a>
        </TD>
</TR>

<!--
<TR>
        <TD>Heat Index. [ASOS/RWIS]</TD>
        <TD> <a href="../data/heat.gif">Plot</a>
        </TD>
</TR>
-->

<TR bgcolor="#EEEEEE">
        <TD>Ceiling. [ASOS/AWOS]</TD>
        <TD> <a href="/data/ceil.gif">Plot</a>
        </TD>
</TR>


<TR>
        <TD><a href="conditions.php">Current Conditions</a>
  </td><td>
  <a href="/ASOS/current.php">ASOS</a> <b>|</b>
  <a href="/AWOS/current.php">AWOS</a> <b>|</b>
  <a href="/schoolnet/current.php">SchoolNet</a> <b>|</b>
  <a href="/RWIS/current.php">RWIS</a> <b>|</b>
  <a href="/current/neighbors.php">Neighbors</a> 
</TD>
</TR>

<tr bgcolor="#EEEEEE">
	<TD colspan="2"><i><a href="/wx/afos/">NWS Text Product Finder</a></i></TD>
</TR>
</table>

<p><font class="bluet">RADAR Data</font>
<br>

<a href="http://www.meteor.iastate.edu/wx/data/current/mwRAD.gif">MidWest Composite</a>
  &nbsp; | &nbsp; 
<a href="http://www.meteor.iastate.edu/wx/data/current/nationalRAD.gif">National Composite</a>
  &nbsp; | &nbsp; 
<a href="http://mesonet.agron.iastate.edu/GIS/apps/iawarn/iawarn.php">NEXRAD images with warnings!</a>

<table class="page" width="100%">
<tr>
  <th style="text-align: left;" colspan="2">Latest NEXRAD</th>
  <th style="text-align: left;" bgcolor="#EEEEEE">Loops</th>
  <th style="text-align: left;">with Hourly Mesonet</th>
</tr>

<tr>
 <td>
  Davenport, IA
  <br>Des Moines, IA
  <br>LaCrosse, WI
  <br>Minneapolis, MN
  <br>Omaha, NE
  <br>Pleasant Hill, MO
  <br>Sioux Falls, SD
  <br>Aberdeen, SD
  <br>Rapid City, SD
 </td>

  <td>
    <a href="/data/nexrad/DVN_N0R_0.gif">Base Reflect</a>
    <br><a href="/data/nexrad/DMX_N0R_0.gif">Base Reflect</a>
    <br><a href="/data/nexrad/ARX_N0R_0.gif">Base Reflect</a>
    <br><a href="/data/nexrad/MPX_N0R_0.gif">Base Reflect</a>
    <br><a href="/data/nexrad/OAX_N0R_0.gif">Base Reflect</a> 
    <br><a href="/data/nexrad/EAX_N0R_0.gif">Base Reflect</a>
    <br><a href="/data/nexrad/FSD_N0R_0.gif">Base Reflect</a> 
    <br><a href="/data/nexrad/ABR_N0R_0.gif">Base Reflect</a> 
    <br><a href="/data/nexrad/UDX_N0R_0.gif">Base Reflect</a> 
  </td>
  <td bgcolor="#EEEEEE">
    <a href="/data/nexrad/NIDSloop.php?site=DVN&product=N0R">Base Ref</a> &nbsp; | &nbsp; <a href="/data/nexrad/NIDSloop.php?site=DVN&product=N0V">Base Vel</a>
    <br><a href="/data/nexrad/NIDSloop.php?site=DMX&product=N0R">Base Ref</a> &nbsp; | &nbsp; <a href="/data/nexrad/NIDSloop.php?site=DMX&product=N0V">Base Vel</a>
    <br><a href="/data/nexrad/NIDSloop.php?site=ARX&product=N0R">Base Ref</a> &nbsp; | &nbsp; <a href="/data/nexrad/NIDSloop.php?site=ARX&product=N0V">Base Vel</a>
    <br><a href="/data/nexrad/NIDSloop.php?site=MPX&product=N0R">Base Ref</a> &nbsp; | &nbsp; <a href="/data/nexrad/NIDSloop.php?site=MPX&product=N0V">Base Vel</a>
    <br><a href="/data/nexrad/NIDSloop.php?site=OAX&product=N0R">Base Ref</a> &nbsp; | &nbsp; <a href="/data/nexrad/NIDSloop.php?site=OAX&product=N0V">Base Vel</a>
    <br><a href="/data/nexrad/NIDSloop.php?site=EAX&product=N0R">Base Ref</a> &nbsp; | &nbsp; <a href="/data/nexrad/NIDSloop.php?site=EAX&product=N0V">Base Vel</a>
    <br><a href="/data/nexrad/NIDSloop.php?site=FSD&product=N0R">Base Ref</a> &nbsp; | &nbsp; <a href="/data/nexrad/NIDSloop.php?site=FSD&product=N0V">Base Vel</a>
    <br><a href="/data/nexrad/NIDSloop.php?site=ABR&product=N0R">Base Ref</a> &nbsp; | &nbsp; <a href="/data/nexrad/NIDSloop.php?site=ABR&product=N0V">Base Vel</a>
    <br><a href="/data/nexrad/NIDSloop.php?site=UDX&product=N0R">Base Ref</a> &nbsp; | &nbsp; <a href="/data/nexrad/NIDSloop.php?site=UDX&product=N0V">Base Vel</a>

 </td>
 <td valign="top">
    <a href="/data/DVN_radar.gif">Davenport</a>
    <br><a href="/data/DMX_radar.gif">Des Moines</a>
    <br><a href="/data/ARX_radar.gif">LaCrosse</a>
    <br><a href="/data/MPX_radar.gif">Minneapolis</a>
    <br><a href="/data/OAX_radar.gif">Omaha</a> 
    <br><a href="/data/EAX_radar.gif">Pleasant Hill</a>
    <br><a href="/data/FSD_radar.gif">Sioux Falls</a> 
    <br><a href="/data/ABR_radar.gif">Aberdeen</a> 
    <br><a href="/data/UDX_radar.gif">Rapid City</a> 
 </td>

</tr>
<tr><td>&nbsp;</td></tr>
</table>

<!-- Begin two column for gridded data and UA -->
<table class="page">
<tr><td class="top">

<font class="bluet">Gridded Surface Plots:</font><br />

  <br><a href="/data/0surfaceTW.gif">Temps & Winds</a>  &nbsp; 
         <a href="/data/SFloop.php?product=TW">Loop</a>
  <br><a href="/data/0surfaceDW.gif">Dew Points & Winds</a>   &nbsp; 
         <a href="/data/SFloop.php?product=DW">Loop</a>
  <br><a href="/data/0surfaceTE.gif">Theta E & Winds</a>  &nbsp; 
         <a href="/data/SFloop.php?product=TE">Loop</a>
  <br><a href="/data/0surfaceMD.gif">Moisture Divergence</a>  &nbsp; 
         <a href="/data/SFloop.php?product=MD">Loop</a>
  <br><a href="/data/0surfaceFRNT.gif">Frontogensis</a>  &nbsp; 
         <a href="/data/SFloop.php?product=FRNT">Loop</a>
  <br><a href="/data/0surfaceDIV.gif">Divergence</a>  &nbsp; 
         <a href="/data/SFloop.php?product=DIV">Loop</a>


</td><td valign="top">
<font class="bluet">Other Data Links:</font><br />
<br><a href="http://www.rap.ucar.edu/weather/upper/sla_wp.gif">Slater Profiler</a>
<br><a href="http://www.rap.ucar.edu/weather/surface/">RAP Surface Page</a>

<p>Soundings:<br>
<br><a href="http://www.rap.ucar.edu/weather/upper/dvn.gif">Davenport</a>
<br><a href="http://www.rap.ucar.edu/weather/upper/oax.gif">Omaha</a>
<br><a href="http://www.rap.ucar.edu/weather/upper/mpx.gif">Minneapolis</a>
<br><a href="http://www.rap.ucar.edu/weather/upper/top.gif">Topeka</a>

</td></tr>
</table>


<?php include("../include/footer2.php"); ?>
