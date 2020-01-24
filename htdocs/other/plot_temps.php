<?php
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("../../include/network.php");
$nt = new NetworkTable("OT");
$cities = $nt->table;

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");
$station = isset($_GET["station"]) ? $_GET["station"]: "OT0002";

$myTime = mktime(0,0,0,$month, $day, $year);

$dirRef = strftime("%Y_%m/%d", $myTime);
$titleDate = strftime("%b %d, %Y", $myTime);

$db = iemdb("other");
$rs = pg_prepare($db, "SELECT",  "SELECT * from t${year} WHERE station = $1 and date(valid) = $2 ORDER by valid ASC");
$rs = pg_execute($db, "SELECT", Array($station, strftime("%Y-%m-%d", $myTime)));

$tmpf = array();
$dwpf = array();
$srad = array();
$times = array();


for($i=0; $row = pg_fetch_array($rs); $i++){
  $tmpf[] = $row["tmpf"];
  $dwpf[] = $row["dwpf"];
  $srad[] = $row["srad"];
  $times[] = strtotime( $row["valid"] );

} // End of while

include ("../../include/jpgraph/jpgraph.php");
include ("../../include/jpgraph/jpgraph_line.php");
include ("../../include/jpgraph/jpgraph_date.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300);
$graph->SetScale("datelin");
$graph->SetY2Scale("lin",0,1000);

$graph->img->SetMargin(65,55,45,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
//$graph->xaxis->SetTextLabelInterval(60);

$graph->xaxis->SetLabelAngle(90);
$graph->yaxis->scale->ticks->Set(2,1);
//$graph->yscale->SetGrace(10);
$graph->title->Set("Temperatures & Solar Radiation for ". $cities[$station]['name']);
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.15,0.11);

//[DMF]$graph->y2axis->scale->ticks->Set(100,25);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");

$graph->y2axis->SetTitle("Solar Radiation [W m**-2]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
$graph->y2axis->SetTitleMargin(40);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($tmpf, $times);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($dwpf, $times);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");

// Create the linear plot
$lineplot3=new LinePlot($srad, $times);
$lineplot3->SetLegend("Solar Rad");
$lineplot3->SetColor("black");

$graph->Add($lineplot2);
$graph->Add($lineplot);
$graph->AddY2($lineplot3);

$graph->Stroke();

?>
