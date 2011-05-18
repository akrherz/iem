<?php 
include("../../config/settings.inc.php");

$HEADEXTRA = '<link rel="stylesheet" type="text/css" href="http://extjs.cachefly.net/ext-3.3.1/resources/css/ext-all.css"/>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.3.1/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.3.1/ext-all.js"></script>
<script type="text/javascript" src="wfos.js?v=3"></script>
<script type="text/javascript" src="../lsr/Exporter-all.js"></script>
<script type="text/javascript" src="search.js?v=3"></script>';
$THISPAGE ="severe-vtec";
$TITLE = "VTEC Search by County/Zone";
include("$rootpath/include/header.php");
?>
<h3>Search for NWS VTEC Products by County/Zone</h3>

<blockquote>This application allows you to query the IEM archive
of NWS VTEC products.  These products include most of the watch, warnings,
and advisories issued.</blockquote>

<div id="myform"></div>
<br />
<div id="mytable"></div>

<?php include("$rootpath/include/footer.php"); ?>