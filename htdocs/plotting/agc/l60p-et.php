<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connection = iemdb("campbelldaily");

$table1 = $station ."_2004";
$table2 = $station ."_2005";

$queryData = "c930 - c70 as dater, c930 as dater2";
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

$accumm = 0.00;

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{ 
  $temper = $row["dater"];
  $accumm = $accumm + $temper ; 
  $ydata[$i]  = $accumm;
  $xlabel[$i] = $row["valid"];

  $precDay = $row["dater2"];
  if ($precDay > 0){
	$ydata2[$i] = $row["dater2"];
  } else {
	$ydata2[$i] = "-";
  }
}

//  $xlabel = array_reverse( $xlabel );
//  $ydata  = array_reverse( $ydata );
//  $ydata2  = array_reverse( $ydata2 );
//  $ydata3  = array_reverse( $ydata3 );

pg_close($connection);

include ("../../include/agclimateLoc.php");
include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");
include ("../dev/jpgraph_bar.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,350,"example1");
$graph->SetScale("textlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(50,10,45,80);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Last 60 days accumulated (Obs Prec - PET) for  ". $ISUAGcities[ $station]["city"] );

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitle("inches");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Month/Day");
//$graph->y2axis->SetTitle("Solar Radiation [Langleys]");
//$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(35);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

//$graph->y2axis->SetColor("red");
//$graph->yaxis->SetColor("red");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("black");

// Create the linear plot
//$lineplot2=new LinePlot($ydata2);
//$lineplot2->SetColor("red");
//$lineplot2->SetLegend("Solar Rad");

$bplot = new BarPlot($ydata2);
$bplot->SetFillColor("blue");
$bplot->SetLegend("Ob Prec [in]");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($bplot);
//$graph->AddY2($lineplot2);

// Display the graph
$graph->Stroke();
?>

