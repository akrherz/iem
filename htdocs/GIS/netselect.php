<?php
/* Need something to render maps instead of writing to /tmp */
include("../../config/settings.inc.php");

/* Calling with a network is required */
if (! isset($_GET["network"])){ die(); }

include("$rootpath/include/selectWidget.php");
$sw = new selectWidget("", "", $_GET['network']);
$sw->logic($_GET);
$sw->directDrawMap();

?>
