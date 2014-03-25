<?php
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
$t->title = "Time Machine";
define("IEM_APPID", 148);
$t->thispage="archive-tm";
$t->headextra = '
<link rel="stylesheet" type="text/css" href="http://cdn.sencha.com/ext/gpl/4.2.1/resources/css/ext-all.css"/>
<script type="text/javascript" src="http://cdn.sencha.com/ext/gpl/4.2.1/ext-all.js"></script>
<script type="text/javascript" src="static.js?v=16"></script>
';

$t->content = <<<EOF
<p style="margin-bottom: 5px;"><strong>IEM Time Machine:</strong> Adjust sliders 
to select a product of your choice from the archive.</p>
<div id="theform"></div>
<img id="imagedisplay" src="timemachine.png" />
EOF;
$t->render('single.phtml');
?>
