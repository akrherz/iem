<div id="iem-section">
<center><table>
<tr><th><a href="index.phtml">Surface Data</a></th>
<th>RADAR/Sat Data</th>
<th><a href="misc.phtml">Advanced Met Plots</a></th>
<th><a href="camera.phtml">Web Cameras</a></th>
<th>&nbsp;</th>
</tr></table></center></div>

<div id="iem-radar">
<table cellspacing="0" cellpadding="0"><tr class="heading"><td colspan="2">RADAR Data Selector</td></tr>

<tr><td>
<br><img src="http://mesonet.agron.iastate.edu/GIS/apps/radar/mwmosaic.php" USEMAP="#mymap">

<MAP NAME="mymap">
<AREA SHAPE="POLY" COORDS="109,216,187,214,184,331,74,290" 
  HREF="javascript:changeSite('EAX', 'Pleasant Hill, MO');">
<AREA SHAPE="POLY" COORDS="40,145,115,165,115,215,104,215,98,233,61,232" 
  HREF="javascript:changeSite('OAX', 'Omaha, NE');">
<AREA SHAPE="POLY" COORDS="35,90,101,93,117,112,116,160,13,140" 
  HREF="javascript:changeSite('FSD', 'Sioux Falls, SD');">
<AREA SHAPE="POLY" COORDS="117,128,116,213,178,212,178,125" 
  HREF="javascript:changeSite('DMX', 'Des Moines, IA');">
<AREA SHAPE="POLY" COORDS="88,39,214,48,150,127,121,127,101,92,81,90" 
  HREF="javascript:changeSite('MPX', 'Minneapolis, MN');">
<AREA SHAPE="POLY" COORDS="215,54,155,121,178,122,182,150,248,149" 
 HREF="javascript:changeSite('ARX', 'LaCrosse, WI');">
<AREA SHAPE="POLY" COORDS="180,152,180,213,190,212,191,223,249,222,249,150" 
 HREF="javascript:changeSite('DVN', 'Davenport, IA');">
</MAP>

<p><a href="javascript:changeSite('UDX', 'Rapid City, SD');">Rapid City</a> and
<a href="javascript:changeSite('ABR', 'Aberdeen, SD');">Aberdeen</a> are also available.

</td><td valign="top">

<form name="myForm" action="raddisplay.phtml">

<br><i>Enter or select NEXRAD<br>
 by clicking on the map:</i><br>
<input type="text" name="site" size=3 maxsize=3>
<input type="text" name="sname">

<p>Select Product:<br>
<select name="prod">
  <option value="N0R">Base Reflectivity</option>
  <option value="N0R_loop">Base Reflectivity Loop (Java Applet)</option>
  <option value="N0R_loop_nj">Base Reflectivity Loop (JavaScript)</option>
  <option value="N0V">Base Velocity</option>
  <option value="N0V_loop">Base Velocity Loop (Java Applet)</option>
  <option value="N0V_loop_nj">Base Velocity Loop (JavaScript)</option>
  <option value="wiem">Hourly Mesonet Overlay</option>
</select>

<p><input type="submit" value="Show"><input type="reset">

<hr>

<b>Static Composite Maps:</b>
<li><a href="http://www.meteor.iastate.edu/wx/data/current/nationalRAD.gif">US Composite</a></li>
<li><a href="http://www.meteor.iastate.edu/wx/data/current/mwRAD.gif">Upper Midwest Composite</a></li>
<li><a href="/data/mwcomp.phtml">MidWest Composite w/ warnings</a></li>

<br><b>GIS Web-Mapping Apps:</b>
<li><a href="http://db1.mesonet.agron.iastate.edu/GIS/apps/rview/compare.phtml">Iowa RADAR comparisons</a></li>
<li><a href="http://mesonet.agron.iastate.edu/current/mcview.phtml">Current/Archived Composite Loop</a></li>
<li><a href="http://db1.mesonet.agron.iastate.edu/GIS/apps/rview/warnings.phtml">Nationwide NEXRAD w/ warnings.</a></li>
<li><a href="http://db1.mesonet.agron.iastate.edu/GIS/apps/iawarn/iawarn.php">Iowa single site NEXRADS w/ warnings.</a></li>
<li><a href="http://mesonet.agron.iastate.edu/cgi-bin/mapserv/mapserv?map=/home/httpd/html/GIS/apps/warning0/warning0.map">Nationwide NEXRAD with warnings</a></li>

</td></tr>
</table><p>

<TABLE cellspacing="0">
<tr class="heading">
 <td colspan=2>Misc Plots</td>
</tr>
<TR class="odd">
	<TD>Precipitation [NEXRAD]</TD>
	<TD> <a href="/data/nexradPrecip1h.gif">1 hour Estimate</a>
	</TD>
</TR>

<TR class="even">
        <TD>20min Mesonet + DMX NEXRAD</TD>
        <TD> <a href="../data/20radarOverlay_0.gif">Image</a> &nbsp; | &nbsp;
        <a href="../data/20radarLoop.html">Loop</a> &nbsp; | &nbsp;
        <a href="../data/20radarLoop_s.html">Small Loop</a>
        </TD>
</TR>

<TR class="odd">
        <TD>20min Mesonet + Composite NEXRAD</TD>
        <TD> <a href="../data/MWoverlay_0.gif">Image</a> &nbsp; | &nbsp;
        <a href="../data/MWoverlayLoop.html">Loop</a> 
        </TD>
</TR>

<TR class="even">
	<TD>Satellite</TD>
	<TD><a href="http://www.meteor.iastate.edu/wx/data/current/IAsatvis.gif">Visible</a> &nbsp; | &nbsp;
	<a href="http://www.meteor.iastate.edu/wx/data/current/IAsatir.gif">Infared</a> &nbsp; | &nbsp;
  <a href="http://weather.cod.edu/satellite/1km/Iowa.gif">Iowa 1km</a>
	</TD>
</TR>

</table></div>
