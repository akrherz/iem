<?php
$connection = pg_connect("pals","5432","intranet");

$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT to_char(ctime, 'mmdd/HH24MI') as tvalid, (ctime - ptime) as diff from tstncf ORDER by ctime";

$result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

$ydata = array();
$xlabel= array();


$j = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  $tokens = split(":", $row["diff"]);
  $ydata[$i]  = $tokens[1];


  $xlabel[$i] = $row["tvalid"];
}

pg_close($connection);


include ("../dev19/jpgraph.php");
include ("../dev19/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example3");
$graph->SetScale("textlin",0,60);
$graph->img->SetMargin(40,20,50,100);

//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);

$graph->yaxis->scale->ticks->Set(5,1);
$graph->yaxis->scale->ticks->SetPrecision(0);

$interval = intval( sizeof($xlabel) / 48 );
if ($interval > 1 ){
  $graph->xaxis->SetTextLabelInterval(2);
  $graph->xaxis->SetTextTickInterval($interval);
}

$graph->title->Set("UNIDATA IDS PRODUCT LATENCY AT THE IEM");
$graph->subtitle->Set("Latency of 1 minute is normal");
//$graph->subtitle->Set("Total Possible: ". $goal[$network] );
$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle("Latency [minutes]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("UTC Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");
$lineplot->SetFillColor("red");

// Add the plot to the graph
$graph->Add($lineplot);

// Display the graph
$graph->Stroke();
?>

