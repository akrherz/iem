<?php
require '../config/settings.inc.php';
include_once('../include/myview.php');

$t = new MyView();
$t->title = "File Not Found (404)";
$t->content = <<<EOF
<h3>Requested file was not found</h3>
<img src="/images/snoopy503.jpg" class="img-responsive" alt="daryl's Cat" />
EOF;
$t->render('single.phtml');
error_log("404 ". $_SERVER["REQUEST_URI"]);
?>
