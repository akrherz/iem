<?php 
include "../../../config/settings.inc.php";
include "../../../include/myview.php";
include "../../../include/network.php";

$nt = new NetworkTable("ISUSM");

$t = new MyView();
$t->title = "IEM NMP Metadata";

$content = <<<EOF

<h3>IEM NMP Metadata</h3>

EOF;

while (list($k, $v)=each($nt->table)){
	$content .= sprintf("<li><a href='pl_ISUSM_%s.xml'>%s %s</a></li>",
			$k, $k, $v["name"]);
}

$t->content = $content;
$t->render("single.phtml");
?>