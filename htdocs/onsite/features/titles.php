<?php 
include("../../../config/settings.inc.php");
include("../../../include/myview.php");
$t = new MyView();
$t->title = "List of Daily Feature Titles";
include("../../../include/database.inc.php");

$connection = iemdb("mesosite");
$query1 = "SELECT title, good, bad, abstain,
      to_char(valid, 'YYYY-MM-DD') as href
      from feature  ORDER by title ASC";
$result = pg_exec($connection, $query1);
$table = "";
$count = pg_num_rows($result);
for($i = 0; $row = pg_fetch_assoc($result); $i ++) {
	if ($i % 4 == 0) {
		$table .= "<tr>\n";
	}
	$table .= sprintf("<td><a href=\"cat.php?day=%s\">%s</a> 
			<i class=\"green\">%s</i>/<i class=\"red\">%s</i>/%s</td>",
	$row["href"], $row["title"], $row["good"], $row["bad"], $row["abstain"]);
	if (($i+1) % 4 == 0) {
		$table .= "</tr>\n";
	}
}


$t->content = <<<EOF
<style>
.green {
 color: #0f0;
}
.red {
 color: #f00;
}
</style>
<h3>IEM Daily Feature Titles</h3>

<p>The following table lists out all <strong>{$count}</strong> IEM Daily Feature 
titles.  For some unknown reason, the author of these posts decided to make each title 
unique.  The uniqueness is case sensitive!  The numbers listed next to the title
are good votes, bad votes, and abstains.

<table class="table table-condensed table-striped">
{$table}
</tr></table>

EOF;
$t->render('single.phtml');
?>

