<?php
$connection = pg_connect("10.10.10.30","9999","iem");


$ylabel = "Temperature [F]";

$query2 = "SELECT max_tmpf, min_tmpf, to_char(day, 'yy/mm/dd') as tvalid 
  from summary WHERE 
   (day + '60 days'::interval) > CURRENT_TIMESTAMP and date(day) != 'TODAY' and station = '". $station ."'  
  ORDER by tvalid ASC";


$result = pg_exec($connection, $query2);


$ydata = array();
$ydata2 = array();
$xlabel= array();
$mAve1 = array();
$mAve2 = array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
  if ($row["max_tmpf"] > -40 && $row["max_tmpf"] < 140) {
    $ydata[$i]  = $row["max_tmpf"];
  }
  if ($row["min_tmpf"] > -60 && $row["min_tmpf"] < 140) {
    $ydata2[$i] = $row["min_tmpf"];
  }
  $xlabel[$i] = $row["tvalid"];
}

for( $j=0; $j < 59 ; $j++)
{
  if ($j < 9){
   $mAve1[$j] = "";
   $mAve2[$j] = "";
  } else {
  $mAve1[$j] = ( $ydata[$j] + $ydata[$j-1] + $ydata[$j-2] + $ydata[$j-3] + 
		$ydata[$j-4] + $ydata[$j-5] + $ydata[$j-6] + $ydata[$j-7] +
		$ydata[$j-8] + $ydata[$j-9] ) / 10.00 ;

  $mAve2[$j] = ( $ydata2[$j] + $ydata2[$j-1] + $ydata2[$j-2] + $ydata2[$j-3] + 
                $ydata2[$j-4] + $ydata2[$j-5] + $ydata2[$j-6] + $ydata2[$j-7] +
                $ydata2[$j-8] + $ydata2[$j-9] ) / 10.00 ;
  }
}

pg_close($connection);

include ("../jpgraph/jpgraph.php");
include ("../jpgraph/jpgraph_line.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,350,"example1");
$graph->SetScale("textlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,10,45,80);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Last 60 days Hi/Low Temp for  ". $station );

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Year/Month/Day");
//$graph->y2axis->SetTitle( $y2label );
//$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitleMargin(50);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);

//$graph->y2axis->SetColor("blue");
//$graph->yaxis->SetColor("red");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetColor("red");
$lineplot->SetLegend("High");

// Create the linear plot
$lineplot2=new LinePlot($mAve1);
$lineplot2->SetColor("red");
$lineplot2->SetLegend("10 day Ave High");
$lineplot2->SetStyle("dashed");

// Create the linear plot
$lineplot3=new LinePlot($ydata2);
$lineplot3->SetColor("blue");
$lineplot3->SetLegend("Low");

// Create the linear plot
$lineplot4=new LinePlot($mAve2);
$lineplot4->SetColor("blue");
$lineplot4->SetLegend("10 day Ave Low");
$lineplot4->SetStyle("dashed");


$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->Add($lineplot3);
$graph->Add($lineplot4);

// Display the graph
$graph->Stroke();
?>

