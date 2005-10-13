<?php
$connection = pg_connect("localhost","5432","iowa");

if ( strlen($tlength) == 0 ) {
	$tlength = "24";
}

$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT to_char(valid, 'mmdd/HH24MI') as tvalid, * from std_dev WHERE (valid + '". $tlength ." hours'::interval) > CURRENT_TIMESTAMP ORDER by valid";

$result = pg_exec($connection, $query1);
$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();

if ($data == "dwpf"){
 $queryStr = "dwpf_";
 $varname = "Dew Point";

} else{
 $queryStr = "";
 $varname = "Temperature";
}

$j = 0;
for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["aswos_".$queryStr ."dev"];
  $ydata2[$i]  = $row["rwis_".$queryStr ."dev"];
  if ( $i % 3 == 0 ) {
	$xlabel[$j] = $row["tvalid"];
	$j = $j +1;
  }
}


pg_close($connection);


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,10,60,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTextTicks(3);
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.05, 0.1, "right", "top");

$graph->title->Set("Last ". $tlength ." h Standard Deviations for ".$varname." Obs");
$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle($varname." STD_DEV (F)");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("ASOS/AWOS (F)");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("RWIS (F)");
$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

