<?php
 include("../../config/settings.inc.php");
 define("IEM_APPID", 144);
 $phenomena = isset($_GET["phenomena"]) ? $_GET["phenomena"] : "TO";
 $significance = isset($_GET["significance"]) ? $_GET["significance"] : "W";
 $phenomena2 = isset($_GET["phenomena2"]) ? $_GET["phenomena2"] : "TO";
 $significance2 = isset($_GET["significance2"]) ? $_GET["significance2"] : "W";
 $enabled2 = isset($_REQUEST['enabled2']);
 $phenomena3 = isset($_GET["phenomena3"]) ? $_GET["phenomena3"] : "TO";
 $significance3 = isset($_GET["significance3"]) ? $_GET["significance3"] : "W";
 $enabled3 = isset($_REQUEST['enabled3']);
 $phenomena4 = isset($_GET["phenomena4"]) ? $_GET["phenomena4"] : "TO";
 $significance4 = isset($_GET["significance4"]) ? $_GET["significance4"] : "W";
 $enabled4 = isset($_REQUEST['enabled4']);
 
 $year1 = isset($_REQUEST["year1"])? intval($_REQUEST["year1"]): date("Y");
 $year2 = isset($_REQUEST["year2"])? intval($_REQUEST["year2"]): date("Y");
 $month1 = isset($_REQUEST["month1"])? intval($_REQUEST["month1"]): 1;
 $month2 = isset($_REQUEST["month2"])? intval($_REQUEST["month2"]): date("m");
 $day1 = isset($_REQUEST["day1"])? intval($_REQUEST["day1"]): 1;
 $day2 = isset($_REQUEST["day2"])? intval($_REQUEST["day2"]): date("d");
 
 $ts1 = gmmktime(0,0,0, $month1, $day1, $year1);
 $ts2 = gmmktime(0,0,0, $month2, $day2, $year2);
 
 $imgurl = sprintf("wfo_vtec_count_plot.py?phenomena=%s&significance=%s&",
 	$phenomena, $significance);
 if ($enabled2)
 	$imgurl .= sprintf("phenomena2=%s&significance2=%s&",
 		$phenomena2, $significance2);
 if ($enabled3)
 	$imgurl .= sprintf("phenomena3=%s&significance3=%s&",
 		$phenomena3, $significance3);
  if ($enabled4)
 	$imgurl .= sprintf("phenomena4=%s&significance4=%s&",
	 	$phenomena4, $significance4);

  $imgurl .= sprintf("sts=%s&ets=%s", gmdate("Ymd", $ts1), 
  		gmdate("Ymd", $ts2));
  
 $TITLE = "IEM | NWS WWA Product Counts by Year";

 include("../../include/vtec.php"); 
 include("../../include/forms.php");
 include("../../include/header.php"); 
 ?>

 <h3>WWA Product Counts by WFO by Year</h3>
 
 <p>This application generates a map of the number of VTEC encoded Watch, Warning, 
 and Advisory (WWA) events by NWS Forecast Office for a time period of your choice.  
 The archive of products goes back to October 2005.  Note: Not all VTEC products go back to
 2005.  You can optionally plot up to 4 different VTEC phenomena and significance 
 types.
 
 <div class="warning">Please be patient, this app may take 10-30 seconds to
 generate the image!</div>
 
<form method="GET" name="theform">

<table cellpadding='3' cellspacing='0' border='1'>
<tr><th>Enabled:?</th><th>Phenomena</th><th>Significance</th></tr>

<tr>
<td></td>
<td><select name="phenomena">
<?php 
reset($vtec_phenomena);
while (list($key, $value)=each($vtec_phenomena)){
  echo sprintf("<option value='%s'%s>%s</option>\n", $key,
  		($key == $phenomena) ? " SELECTED='SELECTED'": '', $value);
}
?>
</select>
</td>
<td><select name="significance">
<?php 
reset($vtec_significance);
while (list($key, $value)=each($vtec_significance)){
  echo sprintf("<option value='%s'%s>%s</option>\n", $key,
  		($key == $significance) ? " SELECTED='SELECTED'": '', $value);
}
?>
</select>
</td>
</tr>
<tr>
<td><input type='checkbox' name='enabled2' <?php if ($enabled2) echo "checked='checked'"; ?>>Include</input></td>
<td><select name="phenomena2">
<?php 
reset($vtec_phenomena);
while (list($key, $value)=each($vtec_phenomena)){
  echo sprintf("<option value='%s'%s>%s</option>\n", $key,
  		($key == $phenomena2) ? " SELECTED='SELECTED'": '', $value);
}
?>
</select>
</td>
<td><select name="significance2">
<?php 
reset($vtec_significance);
while (list($key, $value)=each($vtec_significance)){
  echo sprintf("<option value='%s'%s>%s</option>\n", $key,
  		($key == $significance2) ? " SELECTED='SELECTED'": '', $value);
}
?>
</select>
</td>
</tr>
<tr>
<td><input type='checkbox' name='enabled3' <?php if ($enabled3) echo "checked='checked'"; ?>>Include</input></td>
<td><select name="phenomena3">
<?php 
reset($vtec_phenomena);
while (list($key, $value)=each($vtec_phenomena)){
  echo sprintf("<option value='%s'%s>%s</option>\n", $key,
  		($key == $phenomena3) ? " SELECTED='SELECTED'": '', $value);
}
?>
</select>
</td>
<td><select name="significance3">
<?php 
reset($vtec_significance);
while (list($key, $value)=each($vtec_significance)){
  echo sprintf("<option value='%s'%s>%s</option>\n", $key,
  		($key == $significance3) ? " SELECTED='SELECTED'": '', $value);
}
?>
</select>
</td>
</tr>

<tr>
<td><input type='checkbox' name='enabled4' <?php if ($enabled4) echo "checked='checked'"; ?>>Include</input></td>
<td><select name="phenomena4">
<?php 
reset($vtec_phenomena);
while (list($key, $value)=each($vtec_phenomena)){
  echo sprintf("<option value='%s'%s>%s</option>\n", $key,
  		($key == $phenomena4) ? " SELECTED='SELECTED'": '', $value);
}
?>
</select>
</td>
<td><select name="significance4">
<?php 
reset($vtec_significance);
while (list($key, $value)=each($vtec_significance)){
  echo sprintf("<option value='%s'%s>%s</option>\n", $key,
  		($key == $significance4) ? " SELECTED='SELECTED'": '', $value);
}
?>
</select>
</td>
</tr>
<tr><th colspan='3'>Time Period (UTC Dates)</th></tr>
<tr><td colspan='3'><strong>Start Date:</strong>
  <?php yearSelect2(2005, $year1, 'year1'); ?>
  <?php monthSelect2($month1, 'month1'); ?>
  <?php echo daySelect2($day1, 'day1'); ?>  
  </td></tr>
<tr><td colspan='3'><strong>End Date:</strong>
  <?php yearSelect2(2005, $year2, 'year2'); ?>
  <?php monthSelect2($month2, 'month2'); ?>
  <?php echo daySelect2($day2, 'day2'); ?> (exclusive)  
  </td></tr>
  </table>

<p><input type="submit" value="Generate Map" />
</form>

<p>Once generated, the map will appear below...
<p><img src="<?php echo $imgurl; ?>" alt="The Map" />

<?php include("../../include/footer.php"); ?>
