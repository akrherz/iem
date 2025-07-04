<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
$t = new MyView();
$t->title = "Referenced By";

$table = "";
$pgconn = iemdb("mesosite");
$rs = pg_query(
    $pgconn,
    "SELECT * from website_citations ORDER by publication_date DESC"
);

$XREF = array(
    "ARCHIVE" => "/archive/",
    "ASOS" => "/request/download.phtml",
    "ASOS1MIN" => "/request/asos/1min.phtml",
    "CLIMODAT" => "/climodat/",
    "COW" => "/cow/",
    "HADS" => "/request/dcp/fe.phtml",
    "IEMRE" => "/iemre/",
    "ISUSM" => "/agclimate/",
    "LSR" => "/request/gis/lsrs.phtml",
    "MOS" => "/mos/",
    "MOSAIC" => "/docs/nexrad_mosaic",
    "NWSTEXT" => "/nws/text.php",
    "PIREPS" => "/request/gis/pireps.php",
    "RAOB" => "/archive/raob/",
    "RWIS" => "/request/rwis/fe.phtml",
    "VTEC" => "/request/gis/watchwarn.phtml",
    "WINDROSE" => "/archive/",
);
$COUNTS = array();

$year = "";
$total = pg_num_rows($rs);
while ($row = pg_fetch_assoc($rs)) {
    $resource = $row["iem_resource"];
    if (!array_key_exists($resource, $COUNTS)) {
        $COUNTS[$resource] = 0;
    }
    $COUNTS[$resource] += 1;
    if ($year != substr($row["publication_date"], 0, 4)) {
        $year = substr($row["publication_date"], 0, 4);
        $table .= sprintf("<tr><td colspan=\"4\"><h3>%s</h3></td></tr>\n", $year);
    }
    $table .= sprintf(
        "<tr><td><a href=\"%s\" class=\"btn btn-primary\">%s</a></td>" .
            "<td><a href=\"%s\">%s</a></td><td>%s</td></tr>\n",
        $XREF[$resource],
        $resource,
        $row["link"],
        $row["publication_date"],
        $row["title"],
    );
}
$tags = "";
// sort by count
arsort($COUNTS);
foreach ($COUNTS as $key => $value) {
    $tags .= sprintf(
        "<a href=\"%s\" class=\"btn btn-primary\">%s (%s)</a> &nbsp; ",
        $XREF[$key],
        $key,
        $value
    );
}
$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
<li class="breadcrumb-item"><a href="/info/">IEM Information</a></li>
<li class="breadcrumb-item active" aria-current="page">Referenced By</li>
</ol>
</nav>

<div class="card mb-4">
<div class="card-header">
<h3 class="mb-0">Scholar Work Referencing IEM</h3>
</div>
<div class="card-body">
<p>Beginning in late 2024, the IEM has attempted to curate a list of scholarly
products referencing datasets found on this website.  The backfilling of
this list remains a work in progress!</p>

<p>There are currently <strong>{$total}</strong> references in this list.
Each entry includes a tag for the IEM resource referenced.  Here is how
many times each tag is used.</p>

<div class="mb-3">
{$tags}
</div>
</div>
</div>

<div class="card">
<div class="card-body">
<div class="table-responsive">
<table class="table table-striped">
<thead class="table-dark sticky-top">
<tr>
  <th>IEM Resource</th>
  <th>Publication Date/Link</th>
  <th>Title</th>
</tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
</div>
</div>
</div>

EOM;
$t->render('single.phtml');
