<?php
require '../config/settings.inc.php';
include_once('../include/myview.php');

$t = new MyView();
$t->title = "File Not Found (404)";
$t->content = <<<EOF
<h3>Requested file was not found</h3>
<img src="/images/cow404.jpg" class="img img-responsive" alt="404 Cow" />
EOF;
$t->render('single.phtml');
$ref = isset($_SERVER["HTTP_REFERER"]) ? $_SERVER["HTTP_REFERER"] : 'none';
error_log("404 ". $_SERVER["REQUEST_URI"]. ' referer: '. $ref);
?>
