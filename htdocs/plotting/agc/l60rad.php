<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("ISUAG");
$ISUAGcities = $nt->table;

$connection = iemdb("isuag");

$station = isset($_GET['station']) ? $_GET["station"]: "A130209";


// Load up climatology
$rs = pg_prepare($connection, "SELECT1", "select to_char(valid, 'mmdd') as d, " .
		"avg(c30) as soil, avg(c80) as srad, count(*) as years from daily " .
		"WHERE station = $1 GROUP by d");
$rs = pg_execute($connection, "SELECT1", Array($station));
$climate = Array();
for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  $climate[ $row["d"] ] = $row;
}

// Fetch Obs
$rs = pg_prepare($connection, "SELECT", "SELECT c30 as soil, c80 as srad, " .
		"valid from daily WHERE station = $1 and  " .
		"(valid + '60 days'::interval) > CURRENT_TIMESTAMP  " .
		"ORDER by valid ASC");
$result = pg_execute($connection, "SELECT", Array($station));

$soil = array();
$c_soil = array();
$srad = array();
$c_srad = array();
$times = array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  $ts = strtotime( $row["valid"] );
  $key = date('md', $ts);
  $c_soil[] = $climate[$key]["soil"];
  $c_srad[] = $climate[$key]["srad"];
  $soil[] = $row["soil"];
  $srad[] = $row["srad"];
  $times[] = $ts;
}

pg_close($connection);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");

// Create the graph. These two calls are always required
$graph = new Graph(640,480);
$graph->SetScale("datelin");
$graph->SetY2Scale("lin",0,1000);
$graph->img->SetMargin(40,40,45,100);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Last 60 daily 4in Soil Temp & Solar Raditaion values for  ". $ISUAGcities[ $station]["name"] );

$graph->title->SetFont(FF_FONT1,FS_BOLD,10);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
//$graph->xaxis->SetTitle("Month/Day");
$graph->y2axis->SetTitle("Solar Radiation [Langleys]");
$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->y2axis->SetColor("red");
//$graph->yaxis->SetColor("red");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");

// Create the linear plot
$lineplot=new LinePlot($soil,$times);
$graph->Add($lineplot);
$lineplot->SetColor("blue");
$lineplot->SetWeight(3);
$lineplot->SetLegend("4in Soil Temp");


// Create the linear plot
$lineplot4=new LinePlot($c_soil,$times);
$graph->Add($lineplot4);
$lineplot4->SetColor("purple");
$lineplot4->SetStyle("dashed");
$lineplot4->SetWeight(2);
$lineplot4->SetLegend("4in Soil Temp Climate");



$bp2=new BarPlot($srad,$times);
$graph->AddY2($bp2);
$bp2->SetFillColor("pink");
$bp2->SetWidth(4.0);
$bp2->SetLegend("Solar Rad");



// Create the linear plot
$lineplot3=new LinePlot($c_srad,$times);
$graph->AddY2($lineplot3);
$lineplot3->SetColor("red");
$lineplot3->SetWeight(2);
$lineplot3->SetStyle("dashed");
$lineplot3->SetLegend("Solar Rad Climate");





// Display the graph
$graph->Stroke();
?>

