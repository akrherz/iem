<?php 
include_once "../../config/settings.inc.php";
//define("IEM_APPID", 85);
$year = isset($_GET["year"]) ? intval($_GET["year"]) : intval(date("Y"));

include_once "../../include/myview.php";
include_once "../../include/vtec.php";
include_once "../../include/forms.php";
include_once "../../include/imagemaps.php";

$uri = sprintf("http://iem.local/json/vtec_max_etn.py?year=%s&format=html", 
		$year);
$table = file_get_contents($uri);

$t = new MyView();
$t->title = "VTEC Event Listing for $year";
$t->headextra = <<<EOM
<link type="text/css" href="/vendor/jquery-datatables/1.10.16/datatables.min.css" rel="stylesheet" />
EOM;

$yselect = yearSelect2(2005, $year, 'year');


$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li class="active">Max VTEC Event Listing</li>
</ol>

<form method="GET" action="maxetn.php">
		Select Year: $yselect
		<input type="submit" value="Generate Table">
</form>
		



{$table}


EOF;
$t->jsextra = <<<EOM
<script src='/vendor/jquery-datatables/1.10.16/datatables.min.js'></script>
<script>
$(document).ready(function(){
    $(".iemdt").DataTable();
});
</script>
EOM;
$t->render("single.phtml");
?>