<?php
// Cool.....

require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";

require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_led.php";

$station = isset($_GET["station"]) ? $_GET["station"] : "DSM";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"]: date("d");

  $myTime = strtotime($year."-".$month."-".$day);

$titleDate = strftime("%b %d, %Y", $myTime);
$sqlDate1 = strftime("%Y-%m-%d 00:00", $myTime);
$sqlDate2 = strftime("%Y-%m-%d 23:59", $myTime);

$connection = iemdb("asos1min");
$rs = pg_prepare($connection, "SELECT", "SELECT ".
	"valid, precip, pres1 from ".
	"alldata_1minute WHERE station = $1 and ".
	"valid >= $2 and valid <= $3 ORDER by valid");

$result = pg_execute($connection, "SELECT", Array($station, $sqlDate1, $sqlDate2));

pg_close($connection);

if (pg_num_rows($result) == 0){
 $led = new DigitalLED74();
 $led->StrokeNumber('NO DATA FOR THIS DATE',LEDC_GREEN);
 die();
}


$prec = array();
$alti = array();
$pvalid = array();
$avalid = array();

for( $p=0; $row = pg_fetch_array($result); $p++)  {
    if ($row["pres1"] !== null) {
        $avalid[] = strtotime($row["valid"]);
        $alti[] = $row["pres1"] * 33.8639;
    }
    if ($row["precip"] !== null){
        $prec[] = $row["precip"];
        $pvalid[] = strtotime($row["valid"]);
    }
} // End of while



// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin", 0, $accumP + 1.00);
$graph->img->SetMargin(55,40,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.07);

//$graph->yaxis->scale->ticks->Set(90,15);
$graph->y2axis->scale->ticks->Set(1,0.25);

$graph->yaxis->SetColor("black");
$graph->yscale->SetGrace(10);
$graph->y2axis->SetColor("blue");

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Station Pressure [mb]");
$graph->y2axis->SetTitle("Accumulated Precipitation [inches]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Central Time Zone");
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(43);
//$graph->y2axis->SetTitleMargin(28);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($alti, $avalid);
$graph->Add($lineplot);
$lineplot->SetLegend("Altimeter");
$lineplot->SetColor("black");

// Create the linear plot
$lineplot2=new LinePlot($prec, $pvalid);
$graph->AddY2($lineplot2);
$lineplot2->SetLegend("Precipitation");
$lineplot2->SetColor("blue");
//$lineplot2->SetFilled();
//$lineplot2->SetFillColor("blue");
$graph->Stroke();
?>
