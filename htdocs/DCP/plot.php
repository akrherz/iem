<?php 
/* I actually generate a plot for us to see!
 * 
 */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable('DCP');
$pgconn = iemdb("hads");

$station = isset($_REQUEST['station']) ? $_REQUEST["station"] : die("No station");
$varname = isset($_REQUEST['var']) ? $_REQUEST['var'] : die("No var");
$sday = isset($_REQUEST['sday']) ? strtotime($_REQUEST['sday']) : die("No sday");
$eday = isset($_REQUEST['eday']) ? strtotime($_REQUEST['eday']) : die("No eday");

$rs = pg_prepare($pgconn, "SELECT", "SELECT * from raw". date("Y", $sday) ." 
	WHERE station = $1 and valid BETWEEN $2 and $3 and key = $4
	ORDER by valid ASC");

$rs = pg_execute($pgconn, "SELECT", Array($station, 
	date('Y-m-d', $sday), date('Y-m-d', $eday), $varname));

$data = Array();
$times = Array();
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
	$times[] = strtotime($row["valid"]);
	$data[] = $row["value"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

$graph = new Graph(640,480);
$graph->SetScale("datelin");
$graph->img->SetMargin(40,40,45,100);

$title = sprintf("%s [%s] Plot of SHEF Variable [%s]", $nt->table[$station]['name'],
	$station, $varname);
$graph->title->Set($title);

$graph->title->SetFont(FF_FONT1,FS_BOLD,10);
$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
//$graph->xaxis->SetTitle("Month/Day");

$graph->xaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetLabelAngle(90);



// Create the linear plot
$lineplot=new LinePlot($data,$times);
$lineplot->SetColor("red");
$lineplot->SetWeight(2);
$graph->Add($lineplot);


// Display the graph
$graph->Stroke();

?>