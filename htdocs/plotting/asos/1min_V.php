<?php
// 1 minute schoolnet data plotter
// Cool.....
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
$nt = new NetworkTable(Array("IA_ASOS","NE_ASOS","IL_ASOS","SD_ASOS"));
$cities = $nt->table;
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_scatter.php";
require_once "../../../include/jpgraph/jpgraph_led.php";

$station = isset($_GET["station"]) ? xssafe($_GET["station"]): "";
$year = get_int404("year", date("Y", time() - 86400));
$month = get_int404("month", date("m", time() - 86400));
$day = get_int404("day", date("d", time() - 86400));

  $myTime = strtotime($year."-".$month."-".$day);

$titleDate = strftime("%b %d, %Y", $myTime);
$sqlDate1 = strftime("%Y-%m-%d 00:00", $myTime);
$sqlDate2 = strftime("%Y-%m-%d 23:59", $myTime);

$connection = iemdb("asos1min");
$rs = pg_prepare($connection, "SELECT", "SELECT " .
		"valid, sknt, drct from " .
		"alldata_1minute WHERE station = $1 and " .
		"valid >= $2 and valid <= $3 ORDER by valid");

$result = pg_execute($connection, "SELECT", Array($station, $sqlDate1, $sqlDate2));

pg_close($connection);
if (pg_num_rows($result) == 0){
 $led = new DigitalLED74();
 $led->StrokeNumber('NO DATA FOR THIS DATE',LEDC_GREEN);
 die();
}

$valid = array();
$smph = array();
$drct = array();
for( $p=0; $row = pg_fetch_array($result); $p++)  {
    $valid[] = strtotime($row["valid"]);
    $smph[] = $row["sknt"] * 1.15;
    $drct[] = $row["drct"];

} // End of while

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datlin",0, 360);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(55,40,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($cities[$station]['name'] ." Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.07);

$graph->yaxis->scale->ticks->Set(90,15);

$graph->yaxis->SetColor("blue");
$graph->y2axis->SetColor("red");

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Wind Direction");
$graph->y2axis->SetTitle("Wind Speed [MPH]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(30);
//$graph->y2axis->SetTitleMargin(28);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($smph, $valid);
$graph->AddY2($lineplot);
$lineplot->SetLegend("5 second Wind Speed");
$lineplot->SetColor("red");

// Create the linear plot
$sp1=new ScatterPlot($drct, $valid);
$graph->Add($sp1);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);

$graph->Stroke();
