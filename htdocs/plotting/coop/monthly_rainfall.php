<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$year = isset($_GET['year']) ? intval($_GET["year"]) : 0;
$station = isset($_GET['station']) ? intval($_GET["station"]) : "ia0200";

include("$rootpath/include/network.php");
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;

$connection = iemdb("coop");

$query2 = "SELECT sum(precip) as rainfall, extract(month from valid) as month from climate51
   WHERE station = '$station' GROUP by month ORDER by month ASC";

$result = pg_exec($connection, $query2);

$climate = array();
$zeros = array();
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  $climate[] = $row["rainfall"];
  $zeros[] = 0;
}

$sql = "select month, avg(c) as c from (select year, month, count(*) as c 
    from alldata WHERE stationid = '$station' and precip > 0 
    GROUP by year, month) as foo GROUP by month ORDER by month ASC";
$result = pg_exec($connection, $sql);

$days = array();
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  $days[] = $row["c"];
}

pg_close($connection);

$xlabel = Array("JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC");

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("textlin",0,6);
$graph->SetY2Scale("lin",0,12);
$graph->yaxis->scale->ticks->Set(1,0.25);
$graph->yaxis->SetColor("blue");
$graph->y2axis->SetColor("red");
$graph->y2axis->SetTitle("Precip Days");
$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->y2axis->title->SetColor("red");

$graph->img->SetMargin(50,45,35,35);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Monthly Rainfall Climatology for ". $cities[strtoupper($station)]['name']);
$subt = sprintf("Annual precip of %.2f inches over %.0f days", array_sum($climate), array_sum($days));
$graph->subtitle->Set($subt);

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Precipitation [inches]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitleMargin(35);
$graph->yaxis->title->SetColor("blue");

$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitleMargin(15);

$graph->legend->Pos(0.2, 0.09);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$bp0=new BarPlot($climate);
$bp0->SetFillColor("blue");

$bp1=new BarPlot($days);
$bp1->SetFillColor("red");

$z=new BarPlot($zeros);
$z->SetFillColor("red");

$gbplot = new GroupBarPlot(array($bp0,$z));
$gbplot->SetWidth(0.6);
$graph->Add($gbplot);

$gbplot2 = new GroupBarPlot(array($z,$bp1));
$gbplot2->SetWidth(0.6);
$graph->AddY2($gbplot2);

// Display the graph
$graph->Stroke();
?>

