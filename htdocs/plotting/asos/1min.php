<?php
// 1 minute schoolnet data plotter
// Cool.....
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
$nt = new NetworkTable(Array("IA_ASOS","NE_ASOS","IL_ASOS", "SD_ASOS"));
$cities = $nt->table;
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_led.php";
require_once "../../../include/jpgraph/jpgraph_date.php";

$station = isset($_GET["station"]) ? $_GET["station"] : "DSM";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"]: date("d");

$myTime = strtotime($year."-".$month."-".$day);

$titleDate = strftime("%b %d, %Y", $myTime);
$sqlDate1 = strftime("%Y-%m-%d 00:00", $myTime);
$sqlDate2 = strftime("%Y-%m-%d 23:59", $myTime);

/** Time to get data from database **/
$connection = iemdb("asos1min");
$rs = pg_prepare(
    $connection,
    "SELECT",
    "SELECT valid, tmpf, dwpf from " .
	"alldata_1minute WHERE station = $1 and " .
    "valid >= $2 and valid <= $3 and tmpf is not null and dwpf is not null ".
    "ORDER by valid ASC");

$result = pg_execute($connection, "SELECT", Array($station, $sqlDate1, $sqlDate2));

pg_close($connection);

if (pg_num_rows($result) == 0){
 $led = new DigitalLED74();
 $led->StrokeNumber('NO DATA FOR THIS DATE',LEDC_GREEN);
 die();
}

$tmpf = array();
$dwpf = array();
$valid = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;
$min_yaxis = 100;
$max_yaxis = 0;

for( $p=0; $row = pg_fetch_array($result); $p++)  {
    $tmpf[] = $row["tmpf"];
    $dwpf[] = $row["dwpf"];
    $valid[] = strtotime($row["valid"]);
} // End of while

// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(55,40,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
//$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);

$graph->xaxis->SetLabelAngle(90);
$graph->yscale->SetGrace(10);
$graph->title->Set($cities[$station]['name'] ." Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.07);



$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Temperature [F]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($tmpf, $valid);
$graph->Add($lineplot);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($dwpf, $valid);
$graph->Add($lineplot2);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");

$graph->Stroke();
