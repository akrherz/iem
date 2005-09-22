<?php
$connection = pg_connect("localhost","5432","campbellhourly");

$table = $station ."_2001";

$queryData = "c100 as dater, c300 as dater2, c800";
$y2label = "Temperature [F]";


//if ($plot == "soil"){
//	$queryData = "c300 as dater, c800";
//	$y2label = "4in Soil Temp [F]";
//}

if ( strlen($date) == 0){
	$date = "Yesterday";
}

$query2 = "SELECT ". $queryData .", to_char(day, 'mmdd/HH24') as valid from ". $table ." WHERE 
	date(day) = '". $date ."'::date ORDER by day DESC ";

$result = pg_exec($connection, $query2);

$ydata = array();
$ydata2 = array();
$ydata3 = array();
$xlabel= array();
$line32 = array();


for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $ydata[$i]  = $row["c800"];
  $ydata2[$i]  = $row["dater"];
  $ydata3[$i] = $row["dater2"];
  $xlabel[$i] = $row["valid"];
  $line32[$i] = 32;
}

  $xlabel = array_reverse( $xlabel );
  $ydata  = array_reverse( $ydata );
  $ydata2  = array_reverse( $ydata2 );
  $ydata3  = array_reverse( $ydata3 );

pg_close($connection);

include ("../../include/agclimateLoc.php");
include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(300,300,"example1");
$graph->SetScale("textlin", 0, 700);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,40,50,80);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($date ." Solar Rad & Temps for  ". $ISUAGcities[ $station]["city"] );

$graph->yaxis->scale->ticks->Set(100,25);
$graph->yaxis->scale->ticks->SetPrecision(0);


$graph->title->SetFont(FF_VERDANA,FS_BOLD,10);
$graph->yaxis->SetTitle("Solar Radiation [kilo-calorie m**-2]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->y2axis->SetTitle( $y2label );
$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);

//$graph->y2axis->SetColor("blue");
$graph->yaxis->SetColor("red");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");
$lineplot->SetLegend("Solar Rad");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("Air Temp");

// Create the linear plot
$lineplot3=new LinePlot($ydata3);
$lineplot3->SetColor("green");
$lineplot3->SetLegend("4in Soil Temp");

// Create the linear plot
$lineplot4=new LinePlot($line32);
$lineplot4->SetColor("black");


$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");
$graph->legend->SetFont(FF_ARIAL,FS_BOLD,10);

// Add the plot to the graph
$graph->Add($lineplot);
$graph->AddY2($lineplot2);
$graph->AddY2($lineplot3);
$graph->AddY2($lineplot4);

// Display the graph
$graph->Stroke();
?>

