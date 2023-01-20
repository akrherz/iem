<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/sites.php";
require_once "../../include/myview.php";

$ctx = get_sites_context();
// boilerplate is used in rendering :/
$station = $ctx->station;
$network = $ctx->network;
$metadata = $ctx->metadata;

$t = new MyView();
$t->title = "Site Neighbors";
$t->sites_current = "neighbors";

$t->content = <<<EOF
<h3>Neighboring Stations</h3>
<p>The following is a list of IEM tracked stations within roughly a 0.25 degree
radius circle from the station location. Click on the site name for more information.</p>

{$ctx->neighbors()}
EOF;
$t->render('sites.phtml');
