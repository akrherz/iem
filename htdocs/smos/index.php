<?php
include("../../config/settings.inc.php");
$TITLE = "IEM | SMOS Data";
$THISPAGE="networks-smos";
include("$rootpath/include/forms.php");
include("$rootpath/include/header.php"); 
?>

<h3>Soil Moisture &amp; Ocean Salinity Data</h3>

<p>The IEM is collecting remotely sensed data from the 
<a href="http://www.esa.int/SPECIALS/smos/">SMOS</a> satellite for swaths 
over the Midwest United States.  On some days, this satellite provides data
over Iowa twice per day.

<h4>Download Data</h4>
<form method="GET" action="dl.php" name="dl">
<table>
<tr><th>Latitude (north degree)</th>
	<th><input type="text" name="lat" size="6" value="42.0" /></th></tr>
<tr><th>Longitude (east degree)</th>
	<th><input type="text" name="lon" size="6" value="-93.0" /></th></tr>
	</table>
<table>
  <tr>
    <td></td>
    <th>Year</th><th>Month</th><th>Day</th>
  </tr>

  <tr>
    <th>Start:</th>
    <td>
     <?php echo yearSelect2(2012, 2010, "year1"); ?>
    </td>
    <td>
     <?php echo monthSelect2(1, "month1"); ?>
    </td>
    <td>
     <?php echo daySelect2(1, "day1"); ?>
    </td>
  </tr>

  <tr>
    <th>End:</th>
    <td>
     <?php echo yearSelect2(2012, 2010, "year2"); ?>
    </td>
    <td>
     <?php echo monthSelect2(date("m"), "month2"); ?>
    </td>
    <td>
     <?php echo daySelect2(1, "day2"); ?>
    </td>
  </tr>
</table>

<input type="submit" value="Get Data!" />
	
	</form>

<p><h4>Recent Plots</h4>
<img src="/data/smos_iowa_sm00.png" />
<br />
<img src="/data/smos_iowa_sm12.png" />
<?php include("$rootpath/include/footer.php"); ?>
