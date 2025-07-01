<?php
require_once "../config/settings.inc.php";
require_once "../include/myview.php";
$t = new MyView();
define("IEM_APPID", 39);
require_once "../include/database.inc.php";
$dbconn = iemdb("mesosite");

$t->title = "Application Listing";
$t->jsextra = <<<EOM
<script src="apps.module.js" type="module"></script>
EOM;

$table = "";
$tags = Array();
$rs = pg_exec(
    $dbconn,
    "SELECT appid, string_agg(tag, ',') as t from iemapps_tags ".
    "GROUP by appid"
);
for ($i=0;$row=pg_fetch_assoc($rs);$i++){
    $tags[$row["appid"]] = $row["t"];
}
$rs = pg_exec($dbconn, "SELECT * from iemapps i ORDER by appid ASC");
while ($row=pg_fetch_assoc($rs)){
    $tt = "";
    if (array_key_exists($row["appid"], $tags)){
        $tt = $tags[$row["appid"]];
    }
    $table .= sprintf(
        "<tr><th><a href='%s'>%s</a></th><td>%s</td><td>%s</td></tr>\n", 
        $row["url"],  $row["name"], $row["description"], $tt);
}

$t->content = <<<EOM
 <h3>IEM Application Listing</h3>
 <p>This website contains a large number of 'applications' which allow for
 dynamic query and product generation.  This page displays a listing of these
 apps along with a brief description.  The tags shown are used to organize the
 apps.</p>

 <div class="mb-3">
   <input type="text" id="appFilter" class="form-control" placeholder="Filter applications by keyword..." />
 </div>

 <table class="table table-striped table-bordered" id="table1">
 <thead>
 <tr><th>Title</th><th>Description</th><th>Tags</th></tr>
 </thead>
 <tbody>
{$table}
 </tbody>
</table>
EOM;
$t->render('single.phtml');
