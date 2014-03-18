<?php
 include("../../config/settings.inc.php");
 include("../../include/myview.php");
 $t = new MyView();
 define("IEM_APPID", 143);
 $phenomena = isset($_GET["phenomena"]) ? $_GET["phenomena"] : "TO";
 $significance = isset($_GET["significance"]) ? $_GET["significance"] : "W";
 
 $imgurl = sprintf("days_since_%s_%s.png", $phenomena,  $significance);
 
 $t->title = "Days Since NWS WWA Product";

 include("../../include/vtec.php"); 

 reset($vtec_phenomena);
$pselect = "";
 while (list($key, $value)=each($vtec_phenomena)){
 	$pselect .= sprintf("<option value='%s'%s>%s</option>\n", $key,
 			($key == $phenomena) ? " SELECTED='SELECTED'": '', $value);
 }
 
 reset($vtec_significance);
$sselect = "";
 while (list($key, $value)=each($vtec_significance)){
 	$sselect .= sprintf("<option value='%s'%s>%s</option>\n", $key,
 			($key == $significance) ? " SELECTED='SELECTED'": '', $value);
 }
 
 
$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li class="active">Days since Last WWA by WFO</li>
</ol>
 <h3>Days since Last WWA Product by WFO</h3>
 
 <p>This application generates a map of the number of days since the issuance
 of a particular VTEC encoded Watch, Warning, and Advisory (WWA) by NWS Forecast 
 Office.  The archive of products goes back to October 2005 and the image is 
 current up until the time reported on the plot.
 
 <div class="alert alert-warning">Please be patient, this app may take 10-30 seconds to
 generate the image!  For performance reasons, this application does cache an
 image for 30 minutes before regenerating it using live data.</div>
 
<form method="GET" name="theform">

<table>
<tr><th>Phenomena</th><th>Significance</th></tr>
<tr>
<td><select name="phenomena">
{$pselect}
</select>
</td>
<td><select name="significance">
{$sselect}
</select>
</td>

</tr>
</table>

<p><input type="submit" value="Generate Map" />
</form>

<p>Once generated, the map will appear below...
<p><img src="{$imgurl}" alt="The Map" class="img img-responsive"/>
EOF;
$t->render('single.phtml');
?>
