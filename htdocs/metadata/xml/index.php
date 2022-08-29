<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/network.php";

$nt = new NetworkTable("ISUSM");

$t = new MyView();
$t->title = "IEM NMP Metadata";

$content = <<<EOF

<h3>IEM NMP Metadata</h3>

EOF;

foreach ($nt->table as $k => $v) {
    $content .= sprintf(
        "<li><a href='pl_ISUSM_%s.xml'>%s %s</a></li>",
        $k,
        $k,
        $v["name"]
    );
}

$t->content = $content;
$t->render("single.phtml");
