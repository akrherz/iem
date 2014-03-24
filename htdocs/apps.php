<?php
require_once "../config/settings.inc.php";
include_once "../include/myview.php";
$t = new MyView();
define("IEM_APPID", 39);
include_once "../include/database.inc.php";
$dbconn = iemdb("mesosite");
 
$t->title = "Application Listing";
$t->thispage = "iem-apps";

$table = "";
$tags = Array();
$rs = pg_exec($dbconn, "SELECT appid, string_agg(tag, ',') as t from iemapps_tags GROUP by appid");
for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
	$tags[$row["appid"]] = $row["t"];
}
$rs = pg_exec($dbconn, "SELECT * from iemapps i ORDER by appid ASC");
for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
	$table .= sprintf("<tr><th><a href='%s'>%s</a></th><td>%s</td><td>%s</td></tr>\n", 
			$row["url"],  $row["name"], $row["description"], @$tags[$row["appid"]]);
}


$t->content = <<<EOF
 <h3>IEM Application Listing</h3>
 <p>These are applications internally indexed by the IEM.  This list is created to help index content
 on this website.
 
 <p><table class="table table-striped">
 <thead>
 <tr><th>Title</th><th>Description</th><th>Tags</th></tr>
 </thead>
 <tbody>
{$table}
 </tbody>
</table>
EOF;
$t->render('single.phtml');
?> 
