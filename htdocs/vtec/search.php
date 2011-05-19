<?php 
include("../../config/settings.inc.php");

$HEADEXTRA = '<link rel="stylesheet" type="text/css" href="../ext-3.3.3/resources/css/ext-all.css"/>
<script type="text/javascript" src="../ext-3.3.3/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="../ext-3.3.3/ext-all.js"></script>
<script type="text/javascript" src="wfos.js?v=3"></script>
<script type="text/javascript" src="../lsr/Exporter-all.js"></script>
<script type="text/javascript" src="search.js?v=4"></script>';
$THISPAGE ="severe-vtec";
$TITLE = "VTEC Search by County/Zone";
include("$rootpath/include/header.php");
?>
<h3>Search for NWS Watch/Warning/Advisories Products by County/Zone</h3>
<br />
<p>The National Weather Service issues watch, warnings, and advisories (WWA) for counties/parishes.  For 
some products (like winter warnings), they issue for forecast zones.  In many parts of the country, these zones are exactly the 
same as the counties/parishes.  When you get into regions with topography, then zones will start to 
differ to the local counties.</p>
<br />
<p>This application allows you to search the IEM's archive of NWS WWA products.  Our archive is not complete, but
there are no known holes since 12 November 2005.  This archive is of those products that contain VTEC codes, which
are nearly all WWAs that the NWS issues for.</p>

<div id="myform"></div>
<br />
<p>The table will automatically populate below once you make your selections above. Click on the linked Event ID
to get more information on the warning.</p>
<br />
<div id="mytable"></div>

<?php include("$rootpath/include/footer.php"); ?>