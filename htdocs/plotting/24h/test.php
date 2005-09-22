<?php
$connection = pg_connect("localhost","5432","asos");


$query1 = "SELECT date(valid) as tvalid, sum(p01m) as precip from t2001 WHERE 
	station = 'AMW' and date_part('month', valid) = 6 and p01m != -9999 GROUP by tvalid";
$query2 = "SELECT valid, tenday from precip_accum

$result = pg_exec($connection, $query1);

$ydata = array();
$ydata2 = array();
$xlabel= array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["tmpf"];
  $ydata2[$i]  = $row["dwpf"];
  $xlabel[$i] = $row["valid"];
}

  $xlabel = array_reverse( $xlabel );
  $ydata2 = array_reverse( $ydata2 );
  $ydata  = array_reverse( $ydata );
 

pg_close($connection);
pg_close($connection2);


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(350,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(30,10,60,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("24 h Meteogram for ". $station);

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Temp (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("Dwp (F)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

