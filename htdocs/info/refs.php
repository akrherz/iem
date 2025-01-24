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
    "SELECT * from website_citations ORDER by publication_date DESC");

$XREF = Array(
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
    "VTEC" => "/request/gis/watchwarn.phtml",
    "WINDROSE" => "/archive/",
);

$year = "";
$total = pg_num_rows($rs);
while ($row = pg_fetch_assoc($rs)) {
    if ($year != substr($row["publication_date"], 0, 4)) {
        $year = substr($row["publication_date"], 0, 4);
        $table .= sprintf("<tr><td colspan=\"4\"><h3>%s</h3></td></tr>\n", $year);
    }
    $table .= sprintf(
        "<tr><td><a href=\"%s\" class=\"btn btn-primary\">%s</a></td>".
        "<td><a href=\"%s\">%s</a></td><td>%s</td></tr>\n",
        $XREF[$row["iem_resource"]], $row["iem_resource"],
        $row["link"], $row["publication_date"], $row["title"],
    );
}
$t->content = <<<EOM
<ul class="breadcrumb">
<li><a href="/info/">IEM Information</a></li>
<li class="active">Referenced By</li>
</ul>

<h3>Scholar Work Referencing IEM</h3>

<p>Beginning in late 2024, the IEM has attempted to curate a list of scholarly
products referencing datasets found on this website.  The backfilling of
this list remains a work in progress!</p>

<p>There are currently <strong>{$total}</strong> references in this list.</p>

<table class="table table-striped">
<thead class="sticky">
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

EOM;
$t->render('single.phtml');
