<?php
$connection = pg_connect("localhost","5432","asos");
$connection2 = pg_connect("localhost","5432","rwis");


$query1 = "SET TIME ZONE 'GMT'";
$query2 = "SELECT sknt, drct, to_char(valid, 'mmdd/HH24MI') as valid from t2003 WHERE station = '". $station ."' 
	and to_char(valid, 'MI') = '00' and valid + '1 day' > CURRENT_TIMESTAMP ORDER by valid ASC LIMIT 24";

if ( strlen($station) == 3 ) {	
	$result = pg_exec($connection, $query1);
	$result = pg_exec($connection, $query2);
} else {
        $result = pg_exec($connection2, $query1);
        $result = pg_exec($connection2, $query2);
}

$ydata = array();
$ydata2 = array();
$xlabel= array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["sknt"];
  $ydata2[$i]  = $row["drct"];
  $xlabel[$i] = $row["valid"];
}

//  $xlabel = array_reverse( $xlabel );
//  $ydata2 = array_reverse( $ydata2 );
//  $ydata  = array_reverse( $ydata );
 

pg_close($connection);
pg_close($connection2);


include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");
include ("../dev/jpgraph_scatter.php");


// Create the graph. These two calls are always required
$graph = new Graph(400,350,"example1");
$graph->SetScale("textlin", 0, 50);
$graph->yaxis->scale->ticks->Set(5,1);
$graph->yaxis->scale->ticks->SetPrecision(0);
$graph->SetY2Scale("lin", 0, 360);
$graph->y2axis->scale->ticks->Set(30,15);
$graph->y2axis->scale->ticks->SetPrecision(0);
$graph->img->SetMargin(40,40,25,90);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("24 h winds for ". $station);

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle("Wind Speed [knots]");
$graph->y2axis->SetTitle("Direction [N 0]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Time [GMT]");
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

$graph->legend->Pos(0.01, 0.07);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$lineplot=new LinePlot($ydata);
// $lineplot->SetLegend("Temp (F)");
$lineplot->SetColor("red");

// Create the linear plot
$sp1=new ScatterPlot($ydata2);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);
// $lineplot2->SetLegend("Dwp (F)");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->AddY2($sp1);

// Display the graph
$graph->Stroke();
?>

