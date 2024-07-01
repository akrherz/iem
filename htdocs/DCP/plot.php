<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/forms.php";
require_once "../../include/jpgraph/jpgraph.php";
require_once "../../include/jpgraph/jpgraph_line.php";
require_once "../../include/jpgraph/jpgraph_date.php";
$nt = new NetworkTable('IA_DCP');
$pgconn = iemdb("hads");

$station = isset($_REQUEST['station']) ? xssafe($_REQUEST["station"]): die("No station");
$varname = isset($_REQUEST['var']) ? xssafe($_REQUEST['var']): die("No var");
if (strlen($varname) == 7){
    $varname = substr($varname, 0, 6);
}
$sday = isset($_REQUEST['sday']) ? strtotime(xssafe($_REQUEST['sday'])) : die("No sday");
$eday = isset($_REQUEST['eday']) ? strtotime(xssafe($_REQUEST['eday'])) : die("No eday");

$rs = pg_prepare(
    $pgconn,
    "SELECT",
    "SELECT * from raw". date("Y", $sday) .
    " WHERE station = $1 and valid BETWEEN $2 and $3 and key = $4 ".
    "ORDER by valid ASC");

$rs = pg_execute($pgconn, "SELECT", Array($station, 
    date('Y-m-d', $sday), date('Y-m-d', $eday), $varname));

$data = Array();
$times = Array();
for ($i=0;$row=pg_fetch_assoc($rs);$i++){
    $times[] = strtotime($row["valid"]);
    $data[] = $row["value"];
}

$graph = new Graph(640,480);
$graph->SetScale("datelin");

$graph->SetMarginColor('white');

$graph->img->SetMargin(40,40,45,120);

$title = sprintf("%s [%s] \nPlot of SHEF Variable [%s]", $nt->table[$station]['name'],
    $station, $varname);
$graph->title->Set($title);

$graph->xaxis->scale->SetDateFormat("M d h A");

$graph->xaxis->SetTitle( sprintf("Time Interval: %s - %s", date('d M Y', $sday),
        date('d M Y', $eday)) );

$graph->xaxis->SetTitleMargin(90);
$graph->xaxis->SetLabelAngle(90);

// Create the linear plot
$lineplot=new LinePlot($data,$times);
$lineplot->SetColor("red");
$lineplot->SetWeight(2);
$graph->Add($lineplot);

// Display the graph
$graph->Stroke();
