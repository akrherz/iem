<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;

$station = isset($_GET["station"]) ? $_GET["station"] : "ia0200";
$month = isset($_GET["month"]) ? intval($_GET["month"]): date("m");
$day = isset($_GET["day"]) ? intval($_GET["day"]): date("d");

$highs = Array();
$lows = Array();

$coop = iemdb('coop');

$rs = pg_prepare($coop,"SELECT", "SELECT * from alldata WHERE 
       stationid = $1 and sday = $2");
$ts = mktime(12,0,0,$month, $day, 2000);
$sday = sprintf("%02d%02d", $month, $day);
$rs = pg_execute($coop, "SELECT", Array(strtolower($station), $sday));
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $highs[] = $row["high"];
  $lows[] = $row["low"];
}

$ahigh = Array();
$ahigh[] = array_sum($highs) / floatval( sizeof($highs) );
$alow = Array();
$alow[] = array_sum($lows) / floatval( sizeof($lows) );

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480);
$graph->SetScale("lin");
$graph->img->SetMargin(45,10,40,45);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->scale->SetAutoMax(5); 
//$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->SetTitleMargin(10);


$graph->yaxis->SetTitle("High Temperature [F]");
$graph->xaxis->SetTitle("Low Temperature [F]");
$lgnd = sprintf("High/Low Observations %s [%s] on %s", $cities[strtoupper($station)]["name"], $station, date("M d", $ts));
$graph->tabtitle->Set($lgnd);

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.7,0.1, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$sc1=new ScatterPlot($highs, $lows);
$graph->Add($sc1);
$sc1->mark->SetType(MARK_FILLEDCIRCLE);
$sc1->mark->SetFillColor("blue");


$sc2=new ScatterPlot($ahigh, $alow);
$graph->Add($sc2);
$sc2->mark->SetType(MARK_FILLEDCIRCLE);
$sc2->SetLegend("Average");
$sc2->mark->SetFillColor("red");



// Display the graph
$graph->Stroke();
?>
