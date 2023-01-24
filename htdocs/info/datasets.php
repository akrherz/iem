<?php
/*
 * Datasets listing app
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 84);
require_once "../../include/vendor/erusev/parsedown/Parsedown.php";

require_once "../../include/database.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
$mesosite = iemdb("mesosite");
$t = new MyView();

$myid = isset($_GET["id"]) ? xssafe($_GET["id"]) : null;
// Sanitize $myid
if (!is_null($myid)) {
    if (preg_match('/^[a-z_]+$/', $myid) != 1) {
        $myid = null;
    }
}
$t->title = "Datasets :: {$myid}";

function get_text($pageid)
{
    $fn = "../../docs/datasets/{$pageid}.md";
    $Parsedown = new Parsedown();
    $c = $Parsedown->text(file_get_contents($fn));
    $ts = date("F d, Y", filemtime($fn));
    $s = <<<EOF
<div class="panel panel-info">
<div class="panel-body">
{$c}
</div>
<div class="panel-footer">Updated: {$ts} <a href="/info/datasets/{$pageid}.html">Permalink</a></div>
</div>
EOF;
    return $s;
}

$content = "";
$pages = array();
if (is_null($myid)) {
    if ($dh = opendir("../../docs/datasets")) {
        while (($file = readdir($dh)) !== false) {
            if ($file == '.' || $file == '..' || $file == 'template.md') continue;
            $pageid = preg_replace('/\\.[^.\\s]{2,4}$/', '', $file);
            $pages[] = $pageid;
            $content .= get_text($pageid);
        }
    }
} else {
    $content .= get_text($myid);
}
$tags = '';
foreach ($pages as $k => $page) {
    $tags .= sprintf("<a href=\"#%s\" class=\"btn btn-default\">%s</a>", $page, $page);
}
if ($tags == '') {
    $tags = "<a href=\"/info/datasets/\" class=\"btn btn-default\"><i class=\"fa fa-th-list\"></i> List All Datasets</a>";
} else {
    $tags = "<strong>Documented Datasets:</strong> :" . $tags;
}

$t->content = <<<EOF
<ul class="breadcrumb">
<li><a href="/info/">IEM Information</a></li>
<li><a href="/info/datasets/">IEM Dataset Documentation</a></li>
<li class="active">{$myid}</li>
</ul>

{$tags}

{$content}
        
EOF;

$t->render('single.phtml');
