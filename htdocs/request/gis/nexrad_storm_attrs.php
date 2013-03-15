<?php 
include("../../../config/settings.inc.php");
define("IEM_APPID", 109);
$THISPAGE = "gis-";
$TITLE = "IEM | NEXRAD Storm Attributes Shapefiles";
include("$rootpath/include/forms.php");
include("$rootpath/include/imagemaps.php");
include("$rootpath/include/header.php"); ?>

<h3 class="heading">Archived NEXRAD Storm Attributes Shapefiles</h3>

<p>The IEM attempts to process and archive the Storm Attribute Table that is
 produced by the RADARs that are a part of the NEXRAD network.  This page allows
 you to selectively download these attributes from the IEM database in 
 shapefile format. <strong>Holes do exist in this archive!</strong>  If you find
 a data hole and would like it filled, please let us know.
 
<p>The archive behind this application is large, so please be patient after clicking
 the Givme button below.  If you request all RADARs, you can only request up to 
 seven days worth of data.  If you can request a single RADAR, there is no 
 date restriction, but the download will be slow! 

<form method="GET" action="/cgi-bin/request/gis/nexrad_storm_attrs.py">
<h4>Select time interval</h4>
<i>(Times are in UTC.)</i>
<table>
  <tr>
    <th>RADAR Site:</th>
    <td></td>
    <th>Year</th><th>Month</th><th>Day</th>
    <th>Hour</th><th>Minute</th>
  </tr>

  <tr>
  <td rowspan='2'><?php echo networkMultiSelect(Array("NEXRAD", "TMDR"), 'ALL', 
  		Array("ALL"=>"ALL"));?></td>
    <th>Start:</th>
    <td>
     <?php echo yearSelect2(2005, date("Y"), "year1"); ?>
    </td>
    <td>
     <?php echo monthSelect2(0,"month1"); ?>
    </td>
    <td>
     <?php echo daySelect2(0, "day1"); ?>
    </td>
    <td>
     <?php echo gmtHourSelect(0, "hour1"); ?>
    </td>
    <td>
     <?php echo minuteSelect(0, "minute1"); ?>
    </td>
  </tr>

  <tr>
    <th>End:</th>
    <td>
     <?php echo yearSelect2(2005, date("Y"), "year2"); ?>
    </td>
    <td>
     <?php echo monthSelect2(0,"month2"); ?>
    </td>
    <td>
     <?php echo daySelect2(0, "day2"); ?>
    </td>
    <td>
     <?php echo gmtHourSelect(0, "hour2"); ?>
    </td>
    <td>
     <?php echo minuteSelect(0, "minute2"); ?>
    </td>
  </tr>
</table>

<p><input type="submit" value="Giveme shapefile now!">
</form>

<h4>Shapefile DBF schema:</h4>
<pre>
Field 0: Type=C/String, Title=`VALID', Timestamp in UTC
Field 1: Type=C/String, Title=`STORM_ID', 2 character Storm ID
Field 2: Type=C/String, Title=`NEXRAD', 3 character NEXRAD ID
Field 3: Type=N/Integer, Title=`AZIMUTH', Azimuth of storm in degrees from North
Field 4: Type=N/Integer, Title=`RANGE', Range of storm in miles from RDA
Field 5: Type=C/String, Title=`TVS', Tornado Vortex Signature
Field 6: Type=C/String, Title=`MESO', Mesocyclone detection
Field 7: Type=N/Integer, Title=`POSH', Probability of Hail
Field 8: Type=N/Integer, Title=`POH', Probability of Hail
Field 9: Type=N/Double, Title=`MAX_SIZE', Maximum Hail Size inch
Field 10: Type=N/Integer, Title=`VIL', Volume Integrated Liquid kg/m3
Field 11: Type=N/Integer, Title=`MAX_DBZ', max dbZ
Field 12: Type=N/Double, Title=`MAX_DBZ_H', Height of Max dbZ in thousands of feet
Field 13: Type=N/Double, Title=`TOP', Storm Top in thousands of feet
Field 14: Type=N/Integer, Title=`DRCT', Motion Direction degrees from North
Field 15: Type=N/Integer, Title=`SKNT', Speed in knots
Field 16: Type=N/Double, Title=`LAT', Latitude
Field 17: Type=N/Double, Title=`LON', Longitude 
</pre>

<h4>Archive notes:</h4>
<ul>
 <li>Data is missing June 2007 to March 2008</li>
 <li>Data is missing November 2008 to March 2009</li>
 </ul>


<?php include("$rootpath/include/footer.php"); ?>
