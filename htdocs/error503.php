<?php
include("../config/settings.inc.php");
include("../include/myview.php");
$t = new MyView();
$t->title = "Service Unavailable (503)";
$t->content = <<<EOF

<h3>Service is unavailable</h3>

<img src="/images/snoopy503.jpg" />
EOF;
$t->render('single.phtml');
?>
