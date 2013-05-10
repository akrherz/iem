<?php
 include("../../config/settings.inc.php");
 define("IEM_APPID", 143);
 $phenomena = isset($_GET["phenomena"]) ? $_GET["phenomena"] : "TO";
 $significance = isset($_GET["significance"]) ? $_GET["significance"] : "W";
 
 $imgurl = sprintf("days_since_%s_%s.png", $phenomena,  $significance);
 
 $TITLE = "IEM | Days Since NWS WWA Product";

 include("$rootpath/include/vtec.php"); 
 include("$rootpath/include/header.php"); 
 ?>

 <h3>Days since Last WWA Product by WFO</h3>
 
 <p>This application generates a map of the number of days since the issuance
 of a particular VTEC encoded Watch, Warning, and Advisory (WWA) by NWS Forecast 
 Office.  The archive of products goes back to October 2005 and the image is 
 current up until the time reported on the plot.
 
 <div class="warning">Please be patient, this app may take 10-30 seconds to
 generate the image!</div>
 
<form method="GET" name="theform">

<table>
<tr><th>Phenomena</th><th>Significance</th></tr>
<tr>
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

<?php include("$rootpath/include/footer.php"); ?>
