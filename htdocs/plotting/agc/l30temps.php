<?php
$connection = pg_connect("localhost","5432","campbelldaily");

$table1 = $station ."_2004";
$table2 = $station ."_2005";

$queryData = "c11 as dater, c12 as dater2";
$ylabel = "Temperature [F]";


//if ($plot == "soil"){
//	$queryData = "c300 as dater, c800";
//	$y2label = "4in Soil Temp [F]";
//}

$query2 = "SELECT ". $queryData .", to_char(day, 'yy/mm/dd') as valid from ". $table1 ." WHERE 
	(day + '60 days'::interval) > CURRENT_TIMESTAMP  UNION 
	SELECT ". $queryData .", to_char(day, 'yy/mm/dd') as valid from ". $table2 ." WHERE
	(day + '60 days'::interval) > CURRENT_TIMESTAMP ORDER by valid ASC ";

$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$xlabel= array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["dater"];
  $ydata2[$i] = $row["dater2"];
  $xlabel[$i] = $row["valid"];
}

//  $xlabel = array_reverse( $xlabel );
//  $ydata  = array_reverse( $ydata );
//  $ydata2  = array_reverse( $ydata2 );
//  $ydata3  = array_reverse( $ydata3 );

pg_close($connection);

include ("../../include/agclimateLoc.php");
include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(500,350,"example1");
$graph->SetScale("textlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,10,45,80);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Last 60 days Hi/Low Temp for  ". $ISUAGcities[ $station]["city"] );

$graph->title->SetFont(FF_VERDANA,FS_BOLD,12);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitle("Year/Month/Day");
//$graph->y2axis->SetTitle( $y2label );
//$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(49);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);

//$graph->y2axis->SetColor("blue");
//$graph->yaxis->SetColor("red");
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");
$lineplot->SetLegend("High");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("Low");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

