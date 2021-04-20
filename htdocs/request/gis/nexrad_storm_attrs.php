<?php 
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 109);
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";
require_once "../../../include/imagemaps.php";

$t = new MyView();
$t->jsextra = <<<EOF
<script>
$('select[name=station]').change( function() {
	nexrad = $('select[name=station]').val();
	$('#histimage').attr('src', '/pickup/nexrad_attrs/'+nexrad+'_histogram.png');
	window.location.href = "#"+ nexrad;
});

var tokens = window.location.href.split('#');
if (tokens.length == 2 && tokens[1].length == 3){
	$('#histimage').attr('src', '/pickup/nexrad_attrs/'+ tokens[1] +'_histogram.png');
}
</script>
EOF;
$t->title = "Download NEXRAD Storm Attributes Shapefile";
$content = <<<EOF
<h3>Archived NEXRAD Storm Attributes Shapefiles</h3>

<p>The IEM attempts to process and archive the Storm Attribute Table that is
 produced by the RADARs that are a part of the NEXRAD network.  This page allows
 you to selectively download these attributes from the IEM database in 
 shapefile format. <strong>Holes do exist in this archive!</strong>  If you find
 a data hole and would like it filled, please let us know.

<div class="alert alert-warning">The <a href="https://www.ncdc.noaa.gov">National Climatic Data Center</a> now
		has a very impressive archive and interface to download these attributes.
		You can find it on their <a href="https://www.ncdc.noaa.gov/swdi/">Severe
		Weather Data Inventory</a>.  For programic access, check out their 
		<a href="https://www.ncdc.noaa.gov/swdiws/">web services</a>.</div>
		
<p>The archive behind this application is large, so please be patient after clicking
 the Givme button below.  If you request all RADARs, you can only request up to 
 seven days worth of data.  If you can request a single RADAR, there is no 
 date restriction, but the download will be slow! 

<p><a class="btn btn-default" href="#histograms" role="button">
		<i class="fa fa-stats"></i> View Histograms</a>
 
<form method="GET" action="/cgi-bin/request/gis/nexrad_storm_attrs.py">
<h4>Select time interval</h4>
<i>(Times are in UTC.)</i>
<table class="table">
<thead><tr><th>RADAR Site</th><th colspan="6">Time Interval</th>
		<th>Format</th></tr></thead>
<tr>
    <th></th>
	<th></th>
    <th>Year</th><th>Month</th><th>Day</th>
    <th>Hour</th><th>Minute</th>
    <td rowspan="3"><select name="fmt">
		<option value="shp">ESRI Shapefile</option>
		<option value="csv">Comma Delimited</option>
		</select></td>
</tr>

<tr>
  <td rowspan='2'>
EOF;
$content .= networkMultiSelect(Array("NEXRAD", "TWDR"), 'ALL', 
  		Array("ALL"=>"ALL"), "radar") ."</td>
    <th>Start:</th>
    <td>
     ". yearSelect2(2005, date("Y"), "year1") ."
    </td>
    <td>
     ". monthSelect2(0,"month1") ."
    </td>
    <td>
     ". daySelect2(0, "day1") ."
    </td>
    <td>
     ". gmtHourSelect(0, "hour1") ."
    </td>
    <td>
     ". minuteSelect(0, "minute1") ."
    </td>
  </tr>

  <tr>
    <th>End:</th>
    <td>
     ". yearSelect2(2005, date("Y"), "year2") ."
    </td>
    <td>
     ". monthSelect2(0,"month2") ."
    </td>
    <td>
     ". daySelect2(0, "day2") ."
    </td>
    <td>
     ". gmtHourSelect(0, "hour2") ."
    </td>
    <td>
     ". minuteSelect(0, "minute2") ."
    </td>
  </tr>
</table>";

$content .= <<<EOF
<p><input type="submit" value="Giveme data right now!">
</form>

<h4>Shapefile DBF schema:</h4>
<pre>
Field 0: Type=C/String, Title='VALID', Timestamp in UTC
Field 1: Type=C/String, Title='STORM_ID', 2 character Storm ID
Field 2: Type=C/String, Title='NEXRAD', 3 character NEXRAD ID
Field 3: Type=N/Integer, Title='AZIMUTH', Azimuth of storm in degrees from North
Field 4: Type=N/Integer, Title='RANGE', Range of storm in miles from RDA
Field 5: Type=C/String, Title='TVS', Tornado Vortex Signature
Field 6: Type=C/String, Title='MESO', Mesocyclone strength (1=weak,25=strongest)
Field 7: Type=N/Integer, Title='POSH', Probability of Hail
Field 8: Type=N/Integer, Title='POH', Probability of Hail
Field 9: Type=N/Double, Title='MAX_SIZE', Maximum Hail Size inch
Field 10: Type=N/Integer, Title='VIL', Volume Integrated Liquid kg/m3
Field 11: Type=N/Integer, Title='MAX_DBZ', max dbZ
Field 12: Type=N/Double, Title='MAX_DBZ_H', Height of Max dbZ in thousands of feet
Field 13: Type=N/Double, Title='TOP', Storm Top in thousands of feet
Field 14: Type=N/Integer, Title='DRCT', Motion Direction degrees from North
Field 15: Type=N/Integer, Title='SKNT', Speed in knots
Field 16: Type=N/Double, Title='LAT', Latitude
Field 17: Type=N/Double, Title='LON', Longitude 
</pre>

<h4>Archive notes:</h4>
<ul>
 <li>Data is missing June 2007 to March 2008</li>
 <li>Data is missing November 2008 to March 2009</li>
 </ul>

<p><a name="histograms"></a><h3>Attribute Speed &amp; Direction Histograms</h3>

<p>Based on the archive built by the IEM, the following are 2-D Histograms 
comparing RADAR storm attribute speed, direction of travel, and day of the year.
A direction of "west" would represent a storm moving from west to east.

<form id='dyno' name='dyno'>

<p><strong>Select RADAR:</strong> 
EOF;
$content .= networkSelect(Array("NEXRAD", "TWDR"), 
		'DMX') ."
<br />
<img id='histimage' src='/pickup/nexrad_attrs/DMX_histogram.png' alt='Histogram' />

</form>";

$t->content = $content;
$t->render('single.phtml');

?>