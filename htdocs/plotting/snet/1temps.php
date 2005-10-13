<?php
$connection = pg_connect("10.10.10.40","5432","snet");


$query2 = "SELECT tmpf, dwpf, to_char(valid, 'mmdd/HH24MI') as valid from t2004 WHERE station = '". $station ."' 
	and valid + '1 day' > CURRENT_TIMESTAMP ORDER by valid DESC";

$result = pg_exec($connection, $query2);

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


include ("../dev15/jpgraph.php");
include ("../dev15/jpgraph_line.php");
include ("../../include/snetLoc.php");


// Create the graph. These two calls are always required
$graph = new Graph(400,350,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,40,55,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextLabelInterval(3);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("24 h Meteogram for ". $Scities[$station]["city"]);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.01, 0.07);
$graph->legend->SetLayout(LEGEND_HOR);

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

