<?php

$tableName = "t2003";
$dbName = "asos";
if ( strlen($date) == 0) {
  $dbName = "compare";
  if ( strlen($station) == 3 ) {
    $tableName = "transfer";
  } else {
    $tableName = "rtransfer";
  }
} else {
  $tableName = "t2003";
  if ( strlen($station) == 3 ) {
    $dbName = "asos";
  } else {
    $dbName = "rwis";
  } 
}

$connection = pg_connect("localhost","5432", $dbName);


$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT tmpf, dwpf, to_char(valid, 'mmdd/HH24MI') as valid from ". $tableName ." WHERE station = '". $station ."' 
	and to_char(valid, 'MI') = '00' and valid + '1 day' > CURRENT_TIMESTAMP ORDER by valid DESC LIMIT 24";

$result = pg_exec($connection, $query1);
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


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(400,350,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(40,40,55,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("24 h Meteogram for ". $station);

$graph->title->SetFont(FF_VERDANA,FS_BOLD,16);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Time [GMT]");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
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

