<?php
 include("../../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");
 include("$rootpath/include/google_keys.php");
 include("$rootpath/include/imagemaps.php");
 $network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";

$TITLE = "IEM | Site Locator";
$THISPAGE = "iem-sites";
$api = $GOOGLEKEYS[$rooturl]["any"];
$HEADEXTRA = "<script src='http://maps.google.com/maps?file=api&amp;v=2&amp;key=$api'></script>
<script src='http://www.openlayers.org/api/OpenLayers.js'></script>
<script src='${rooturl}/js/olselect.php?network=${network}'></script>";
$BODYEXTRA = "onload=\"init()\"";
include("$rootpath/include/header.php"); 
?>
<style type="text/css">
        #map {
            width: 640px;
            height: 400px;
            border: 2px solid black;
        }
</style>
<h3 class="heading">IEM Site Information</h3><p>
<div class="text">
<p>The IEM collects information from many sites.  These sites are organized into
networks based on their geography and/or the organization who administers the
network.  This application provides some metadata and site specific applications
you may find useful.</p>

<div align="center">

<form name="switcher">
<table>
<tr><th>Select By Network:</th>
<td>
<?php echo selectNetwork($network); ?>
</td>
<td><input type="submit" value="Switch Network"></td>
</tr></table>
</form>

<form name="olselect">
<table>
<tr><th>Select By Station:</th>
<td>
<?php echo networkSelect($network, ""); ?>
</td>
<td><input type="submit" value="Select Station"></td>
</tr></table>
<br />Or select site from this map by clicking on the black dot....
<div id="map"></div>
<div id="sname" unselectable="on">No site selected</div>
</form>


</div>
<br /><br /></div>

<?php include("$rootpath/include/footer.php"); ?>
