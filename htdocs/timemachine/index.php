<?php
include("../../config/settings.inc.php");
$TITLE = "IEM :: Time Machine";
define("IEM_APPID", 148);
$THISPAGE="archive-tm";
$HEADEXTRA = '
<link rel="stylesheet" type="text/css" href="http://cdn.sencha.com/ext/gpl/3.4.1.1/resources/css/ext-all.css"/>
<script type="text/javascript" src="http://cdn.sencha.com/ext/gpl/3.4.1.1//adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="http://cdn.sencha.com/ext/gpl/3.4.1.1/ext-all.js"></script>
<script type="text/javascript" src="static.js?v=14"></script>
';
include("../../include/header.php"); 
?>
<p style="margin-bottom: 5px;"><strong>IEM Time Machine:</strong> Adjust sliders 
to select a product of your choice from the archive.</p>
<div id="theform"></div>
<img id="imagedisplay" src="timemachine.png" />
<?php include("../../include/footer.php"); ?>
