<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Interactive Plotting";
$t->content = <<<EOM
<h3>This page has been depreciated.</h3>

<p>Most of the links found on this page can be found on the <a href="/climate/">Climatology</a> page.
EOM;
$t->render('single.phtml');
