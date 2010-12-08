<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection = iemdb("isuag");
include("$rootpath/include/network.php");
$nt = new NetworkTable("ISUAG");
$ISUAGcities = $nt->table;


$station = $_GET["station"];
$ts = time() - 86400 - 7*3600;

$date = date("Y-m-d", $ts);




$rs = pg_prepare($connection, "SELECT", "SELECT c11 as dater, c12 as dater2, " .
		"to_char(valid, 'yy/mm/dd') as valid from daily WHERE " .
		"station = $1 and (valid + '30 days'::interval) > CURRENT_TIMESTAMP  " .
		"ORDER by valid ASC ");



$result = pg_execute($connection, "SELECT", Array($station));

$ydata = array();
$ydata2 = array();
$xlabel= array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["dater"];
  $ydata2[$i] = $row["dater2"];
  $xlabel[$i] = $row["valid"];
}

pg_close($connection);

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(500,350,"example1");
$graph->SetScale("textlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,10,45,80);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Last 60 days Hi/Low Temp for  ". $ISUAGcities[ $station]["name"] );

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Year/Month/Day");
//$graph->y2axis->SetTitle( $y2label );
//$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(49);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

//$graph->y2axis->SetColor("blue");
//$graph->yaxis->SetColor("red");
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$graph->Add($lineplot);
$lineplot->SetColor("red");
$lineplot->SetLegend("High");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$graph->Add($lineplot2);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("Low");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


// Add the plot to the graph



// Display the graph
$graph->Stroke();
?>

