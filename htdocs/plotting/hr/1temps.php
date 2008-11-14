<?php
include("../../../config/settings.inc.php");
$station = isset($_GET['station']) ? $_GET["station"]: "AMW";
$hours = isset($_GET["hours"]) ? intval($_GET["hours"]): 24;


include("$rootpath/include/database.inc.php");

$connection = iemdb("access");


$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT tmpf, dwpf  
	, valid from current_log WHERE station = '". $station ."' 
	and valid + '".$hours." hours' > CURRENT_TIMESTAMP ORDER by valid ASC";

// $result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$times = array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[]  = $row["tmpf"];
  $ydata2[]  = $row["dwpf"];
  $times[] = strtotime( $row["valid"] );
}

pg_close($connection);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/station.php");
$st = new StationData($station);
$cities = $st->table;


// Create the graph. These two calls are always required
$graph = new Graph(400,350,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(40,40,55,90);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);

$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($hours." h Meteogram for ". $cities[$station]['name']);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
//$graph->xaxis->SetTitle("Local Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetLabelFormatString("M d h A", true);


$graph->legend->Pos(0.01, 0.07);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata, $times);
$lineplot->SetLegend("Temp (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2, $times);
$lineplot2->SetLegend("Dwp (F)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot2);
$graph->Add($lineplot);

// Display the graph
$graph->Stroke();
?>

