<?php 
/* I actually generate a plot for us to see!
 * 
 */
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("../../include/network.php");
require_once "../../include/forms.php";
$nt = new NetworkTable('IA_DCP');
$pgconn = iemdb("hads");

$station = isset($_REQUEST['station']) ? xssafe($_REQUEST["station"]): die("No station");
$varname = isset($_REQUEST['var']) ? xssafe($_REQUEST['var']): die("No var");
$sday = isset($_REQUEST['sday']) ? strtotime($_REQUEST['sday']) : die("No sday");
$eday = isset($_REQUEST['eday']) ? strtotime($_REQUEST['eday']) : die("No eday");

$rs = pg_prepare($pgconn, "SELECT", "SELECT * from raw". date("Y", $sday) ." 
	WHERE station = $1 and valid BETWEEN $2 and $3 and key = $4
	ORDER by valid ASC");

$rs = pg_execute($pgconn, "SELECT", Array($station, 
	date('Y-m-d', $sday), date('Y-m-d', $eday), $varname));

$data = Array();
$times = Array();
for ($i=0;$row=pg_fetch_array($rs);$i++){
	$times[] = strtotime($row["valid"]);
	$data[] = $row["value"];
}

include ("../../include/jpgraph/jpgraph.php");
include ("../../include/jpgraph/jpgraph_line.php");
include ("../../include/jpgraph/jpgraph_date.php");

$graph = new Graph(640,480);
$graph->SetScale("datelin");

$graph->SetMarginColor('white');


$graph->img->SetMargin(40,40,45,100);

$title = sprintf("%s [%s] \nPlot of SHEF Variable [%s]", $nt->table[$station]['name'],
	$station, $varname);
$graph->title->Set($title);

$graph->title->SetFont(FF_VERDANA,FS_BOLD,11);
$graph->subtitle->SetFont(FF_VERDANA,FS_BOLD,20);
$graph->xaxis->title->SetFont(FF_VERDANA,FS_BOLD,11);

$graph->xaxis->scale->SetDateFormat("M d h A");

$graph->xaxis->SetTitle( sprintf("Time Interval: %s - %s", date('d M Y', $sday),
		date('d M Y', $eday)) );

$graph->xaxis->SetTitleMargin(70);
$graph->xaxis->SetLabelAngle(90);



// Create the linear plot
$lineplot=new LinePlot($data,$times);
$lineplot->SetColor("red");
$lineplot->SetWeight(2);
$graph->Add($lineplot);


// Display the graph
$graph->Stroke();

?>