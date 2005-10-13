<?php
$connection = pg_connect("localhost","5432","iowa");

if ( strlen( $tlength) == 0  ){
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

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  
  $ydata[$i]  = $row["aswos_".$queryStr ."avg"];
  $ydata2[$i]  = $row["rwis_".$queryStr ."avg"];
  if ( $i % 3 == 0 ) {
	$xlabel[$j] = $row["tvalid"];
	$j = $j +1 ;
  }
}


$mins = array();
// Dont count ASOS since they have missing values
$mins[0] = min($ydata);
$mins[1] = min($ydata2);
$mins[2] = max($ydata);
$mins[3] = max($ydata2);


$plotmin = min($mins) - 2;
$plotmax = max($mins) + 2;

pg_close($connection);


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example1");
$graph->SetScale("textlin", $plotmin , $plotmax);
$graph->yaxis->scale->ticks->Set(5,1);
$graph->yaxis->scale->ticks->SetPrecision(0);
$graph->img->SetMargin(40,10,50,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetTextTicks(3);
$graph->xaxis->SetPos("min");
$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01, 0.06, "right", "top");
//$graph->legend->SetBackground("white");

$graph->title->Set("Last ". $tlength ." h Average ". $varname ." Obs");
$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle($varname ." (F)");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("GMT Valid Time");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("ASOS+AWOS (F)");
$lineplot->SetColor("red");
//$lineplot->SetColor("black");
//$lineplot->SetStyle("longdashed");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("RWIS (F)");
$lineplot2->SetColor("blue");
//$lineplot2->SetColor("black");
//$lineplot2->SetStyle("solid");


// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

