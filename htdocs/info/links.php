<?php
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
$t->title = "Links";
$t->thispage = "iem-links";
$t->content = <<<EOF

<h3>Links</h3><p>

<div class="row"><div class="col-sm-6">
		
<h3>Other State Mesonets:</h3>
<ul>
 <li><a href="http://www.awis.com/mesonet/index.html">Alabama Mesonet</a></li>
 <li><a href="http://www.georgiaweather.net/">Georgia Environmental Network</a></li>
 <li><a href="http://mesonet.k-state.edu">Kansas Mesonet</a></li>
 <li><a href="http://www.kymesonet.org">Kentucky Mesonet</a></li>
 <li><a href="http://www.met.utah.edu/jhorel/html/mesonet/">Meso West</a></li>
 <li><a href="http://agebb.missouri.edu/weather/">Missouri</a></li>
 <li><a href="http://nysmesonet.org/">New York Mesonet</a></li>
 <li><a href="http://www.mesonet.ou.edu">Oklahoma Mesonet</a></li>
 <li><a href="http://chiliweb.southalabama.edu/">South Alabama Mesonet</a></li>
 <li><a href="http://mesonet.tamu.edu/">Texas Mesonet</a></li>
 <li><a href="http://www.mesonet.ttu.edu/">West Texas Mesonet</a></li>
 <li><a href="http://agwx.soils.wisc.edu/uwex_agwx/awon">Wisconsin Extension AgWeather</a></li>
</ul>
		

<h3>Real Time Air Quality Charts and Maps</h3>

<p>Air pollutant concentrations are monitored for the DNR Air Quality 
Bureau by the University of Iowa Hygienic Laboratory, the Polk County 
Health Dep- artment, and the Linn County Health Department. You can 
access this data in the following locations:</p>

<ul>
<li><A href="http://www.linncleanair.org/Default.aspx">Linn County Health Department</A> (monitors in Linn County, Waterloo, Waverly) </li>

<li><A href="http://www.polkcountyiowa.gov/airquality/">Polk County Air Pollution Control</A> (monitors in Polk County)</li>
<li><A href="http://airnow.gov/">EPA AIRNOW</A>(national maps)</li>
</ul>

<h3>Iowa Links:</h3>
<ul>
 <li><a href="http://www.weatherview.dot.state.ia.us/">Iowa DOT WeatherView</a></li>
 <li><a href="http://www.511ia.org/">Iowa 511 Website</a></li>
</ul>

</div><div class="col-sm-6">
		
<h3>Other Links:</h3>
<ul>
 <li><a href="http://www.iowaagriculture.gov/climatology.asp">Iowa State Climatologist Office</a></li>
 <li><a href="http://205.156.54.206/om/coop/index.htm">National COOP Observer Program</a></li>
 <li><a href="http://www.weatherview.dot.state.ia.us/">Iowa DOT WeatherView</a></li>
 <li><a href="http://www.missouri.edu/~moclimat/">Missouri Climate Center</a></li>
 <li><a href="http://www.crh.noaa.gov/ncrfc/index.html">North Central River Forecast Center</a> NWS</li>
 <li><a href="http://extension.agron.iastate.edu/soils/PDFs/acretrends.pdf">Corn/Soybean Acres planted in Iowa</a></li>
 <li><a href="http://igic.gis.iastate.edu">Iowa GIS Council [IGIC]</a></li>
 <li><a
 href="http://igic.gis.iastate.edu/about/committee/natural-resources">IGIC
 Weather/Climate/Environment Sub-Committee</a></li>
 <li><a href="http://www.uni.edu/storm/">UNI Storm Project</a></li>
 <li><a href="http://hpcc.unl.edu/">High Plains Regional Climate Center</a></li>
 <li><a href="http://has.ncdc.noaa.gov/">NCDC Level II/III RADAR Archive</a></li>
</ul>

<p><h3>Publicity</h3>
<br />Sep 2005, <a href="http://www.unidata.ucar.edu/newsletter/05sep/05sepel.html#Article2">Unidata Newsletter</a>
<br>27 Feb 2004, <a href="http://archive.inside.iastate.edu/2004/0227/weather.shtml">Inside Iowa State</a>
<br>Jan 2004, <a href="http://www.agron.iastate.edu/Agron/News/2003_Agron_Alumni_News_Web.pdf">2003 Agronomy Alumni Newsletter</a>
<br>01 Jul 2003, <a href="http://www.iastate.edu/~nscentral/releases/2003/jul/mesonet.shtml">Iowa State News Service</a>
<br>27 Feb 2003, <a href="http://www.zwire.com/site/news.cfm?newsid=7200551&BRD=1813&PAG=461&dept_id=68588&rfi=6">Iowa Falls Times-Citizen</a>
<br>14 Jan 2003, <a href="http://www.las.iastate.edu/newnews/mesonet.shtml">ISU Liberal Arts & Sciences <i>around LAS</i></a>
<br>12 Dec 2002, <a href="http://www.ag.iastate.edu/aginfo/agaction/agaction.php?date=2002-12-12&function=view">ISU Agricultural Action</a>
<br>November 2002, <a href="http://www.nwas.org/2002awards.html">National Weather Association, Larry R Johnson Award</a>
<br>November 2002, <a href="http://www.cipco.net/images/advocate/200211PDF.pdf">CIPCO Advocate</a>

<p><h3>Misc</h3>

<br>Cool picture of <a href="http://www.ocs.ou.edu/whatsnew/ice_tower.jpg">ice deposition</a> on an Oklahoma Mesonet site.

</div></div>

EOF;
$t->render('single.phtml');
?>
