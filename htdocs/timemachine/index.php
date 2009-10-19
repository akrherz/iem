<?php
include("../../config/settings.inc.php");
$TITLE = "IEM | Time Machine";
$HEADEXTRA = '
<link rel="stylesheet" type="text/css" href="http://extjs.cachefly.net/ext-3.0.0/resources/css/ext-all.css"/>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.0.0/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.0.0/ext-all.js"></script>
<script type="text/javascript" src="static.js?v=0"></script>
';
include("$rootpath/include/header.php"); 
?>
<div id="yearslider"></div>
<div id="dayslider"></div>
<div id="timeslider"></div>
<div id="displaydt"></div>
<img id="imagedisplay" src="../data/mesonet.gif" />

<?php include("$rootpath/include/footer.php"); ?>
