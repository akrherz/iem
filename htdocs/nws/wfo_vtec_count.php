<?php
 include("../../config/settings.inc.php");
 define("IEM_APPID", 144);
 $phenomena = isset($_GET["phenomena"]) ? $_GET["phenomena"] : "TO";
 $significance = isset($_GET["significance"]) ? $_GET["significance"] : "W";
 $year = isset($_REQUEST["year"])? intval($_REQUEST["year"]): date("Y");
 
 $imgurl = sprintf("wfo_vtec_count_%s_%s_%s.png", $year, $phenomena,  
 		$significance);
 
 $TITLE = "IEM | NWS WWA Product Counts by Year";

 include("../../include/vtec.php"); 
 include("../../include/forms.php");
 include("../../include/header.php"); 
 ?>

 <h3>WWA Product Counts by WFO by Year</h3>
 
 <p>This application generates a map of the number of VTEC encoded Watch, Warning, 
 and Advisory (WWA) by NWS Forecast Office for a year.  
 The archive of products goes back to October 2005 and the image is current up 
 until the time reported on the plot.  Note: Not all VTEC products go back to
 2005.
 
 <div class="warning">Please be patient, this app may take 10-30 seconds to
 generate the image!</div>
 
<form method="GET" name="theform">

<table>
<tr><th>Year</th><th>Phenomena</th><th>Significance</th></tr>
<tr>
<td><?php echo yearSelect(2005, $year); ?></td>
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
</table>

<p><input type="submit" value="Generate Map" />
</form>

<p>Once generated, the map will appear below...
<p><img src="<?php echo $imgurl; ?>" alt="The Map" />

<?php include("../../include/footer.php"); ?>
