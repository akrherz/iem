<?php 
 include("../../config/settings.inc.php");
 $TITLE = "ISU Ag Climate";
 $THISPAGE = "networks-agclimate";
 include("$rootpath/include/header.php"); 
 $prod = isset($_GET["prod"]) ? intval($_GET["prod"]) : 1;

$old2new = Array(
 "/data/agclimate/air-temp-out.png" => 1,
 "/data/agclimate/4in-temp-out.png" => 2,
 "/agclimate/daily_pics/4in-temp-out.png" => 2,
 "/data/agclimate/soil-hilo-out.png" => 3,
 "/agclimate/daily_pics/soil-hilo-out.png" => 3,
 "/data/agclimate/rad-out.png" => 4,
 "/data/agclimate/prec-out.png" => 5,
 "/data/agclimate/et-out.png" => 6,
 "/data/agclimate/pk-wind-out.png" => 7,
 "/data/agclimate/avewind-out.png" => 8,
 "/data/agclimate/dwpts.png" => 9,
 "/data/agclimate/mon-et-out.png" => 10,
 "/data/agclimate/mon-prec-out.png" => 11 );

 // Legacy
 if (isset($_GET["src"])){
  $prod = $old2new[$_GET["src"]];
 }

$data = Array(
1 => Array(
 "mapurl" => "$rooturl/data/agclimate/air-temp-out.png",
 "desc" => "High and low air temperature for a local day. Measurements are 
            made at a 2 meter height.",
),
2 => Array(
 "mapurl" => "$rooturl/data/agclimate/4in-temp-out.png",
 "desc" => "Average 4 inch soil depth temperature.  Usually under a 
            bare soil.",
),
3 => Array(
 "mapurl" => "$rooturl/data/agclimate/soil-hilo-out.png",
 "desc" => "High and low 4 inch soil depth temperature.  Usually under a 
            bare soil.",
),
4 => Array(
 "mapurl" => "$rooturl/data/agclimate/rad-out.png",
 "desc" => "Daily total (direct + diffuse) solar radiation.",
),
5 => Array(
 "mapurl" => "$rooturl/data/agclimate/prec-out.png",
 "desc" => "Daily total precipitation.  This is measured with a <b>non-heated</b> tipping bucket located near the ground.  These reported values should be
used with extreme caution.  For various reasons, the reported values are 
often too low.",
),
6 => Array(
 "mapurl" => "$rooturl/data/agclimate/et-out.png",
 "desc" => "Potential maximum estimated evapotranspiration.  This value uses
            a daily Penman formulation with a crop coefficient of 1.",
),
7 => Array(
 "mapurl" => "$rooturl/data/agclimate/pk-wind-out.png",
 "desc" => "Peak 5 second sustained wind gust.  The value is presented along
      with the time using a 24 hour clock.  For example, 18:00 would be 6 PM.
      Values are in local time, either CDT or CST depending on the time of
      year.",
),
8 => Array(
 "mapurl" => "$rooturl/data/agclimate/avewind-out.png",
 "desc" => "Average wind speed for the day as recorded by the data logger
            on the station.",
),
9 => Array(
 "mapurl" => "$rooturl/data/agclimate/dwpts.png",
 "desc" => "High and low dew points for the day."
),
10 => Array(
 "mapurl" => "$rooturl/data/agclimate/mon-et-out.png",
 "desc" => "Monthly total of daily maximum potential evapotranspiration. The
            daily value is calculated via a Penman formulation with a crop
            coefficient of 1.  The value would be a theoretical maximum."
),
11 => Array(
 "mapurl" => "$rooturl/data/agclimate/mon-prec-out.png",
 "desc" => "Monthly total of daily reported precipitation. This is measured with a <b>non-heated</b> tipping bucket located near the ground.  These reported values should be
used with extreme caution.  For various reasons, the reported values are 
often too low."
),
12 => Array(
 "mapurl" => "$rooturl/data/agclimate/chill-sum.png",
 "desc" => "The Standard Chill Unit map is a summation of hours during 
   which the temperature was between 32 and 45 degrees <b>after</b> 
   1 September.  The value has application for 
   fruit growers in the state.  The departure from average is also 
   presented.  This average is computed from the observational record at
   the site."
),
);

?>
<div class="text">

<table style="float: left;" width="100%">
<TR>
<TD valign="top">

<img src="<?php echo $data[$prod]["mapurl"]; ?>" ALT="ISU Ag Climate" style="border: 1px solid #000; ">

<p><strong>Plot Description:</strong><br />
<?php echo $data[$prod]["desc"]; ?>

<p><strong>QC Flags:</strong>
<table>
<tr>
  <th>M</th>
  <td>the data is missing</td></tr>

<tr>
  <th>E</th>
  <td>An instrument may be flagged until repaired</td></tr>

<tr>
  <th>R</th>
  <td>Estimate based on weighted linear regression from surrounding stations</td></tr>

<tr>
  <th>e</th>
  <td>We are not confident of the estimate</td></tr>

</table>


</TD>
<TD valign="TOP" width="250">

	<?php include("include/dataLinks.php"); ?>

</TD></TR>
</table>

<br clear="all" /><p>&nbsp;</p>
</div>

<?php include("$rootpath/include/footer.php"); ?>
