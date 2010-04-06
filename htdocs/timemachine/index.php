<?php
include("../../config/settings.inc.php");
$TITLE = "IEM | Time Machine";
$THISPAGE="archive-tm";
$HEADEXTRA = '
<link rel="stylesheet" type="text/css" href="http://extjs.cachefly.net/ext-3.2.0/resources/css/ext-all.css"/>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.2.0/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.2.0/ext-all.js"></script>
<script type="text/javascript" src="static.js?v=11"></script>
';
include("$rootpath/include/header.php"); 
?>
<p style="margin-bottom: 5px;"><strong>IEM Time Machine:</strong> Adjust sliders to select a product of your choice from the archive.</p>
<div id="theform"></div>
<img id="imagedisplay" src="timemachine.png" />
<?php include("$rootpath/include/footer.php"); ?>
