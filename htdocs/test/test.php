<?php
session_start();
$TITLE = "Iowa Environmental Mesonet";
$HEADEXTRA = "<link rel=\"alternate\" type=\"application/rss+xml\" title=\"RSS feed\" href=\"/rss.php\" />";
 include("/mesonet/php/include/header.php"); ?>

<div id="iem-warning-bar-new"><a 
href="http://mesonet.agron.iastate.edu/GIS/apps/rview/warnings.phtml">There are active NWS warnings in Iowa.</a></div> 

<?php include("/mesonet/php/include/footer.php"); ?>
