<?php
$ydata = array();
$ydata2 = array();
$xlabel= array();


// $fcontents = file('/home/akrherz/TFD.out');
//$fcontents = file('/home/mm5/frost/tfd.out');
$fcontents = file('input/input.2002010100');
$i = 0;
$j = 0;
$k = 0;
while (list ($line_num, $line) = each ($fcontents)) {
     $parts = preg_split ("/[\s,]+/", $line);
     if ( $j % 30 == 0 ){
	    $xlabel[$k] = substr( $parts[1], 0, 16);
//     	    $xlabel[$k] = $parts[1];
	    $k++;
     	}
       	$ydata[$j] = $parts[2];
	$ydata2[$j] = $parts[3];
	$ydata3[$j] = $parts[4];
      $j++;
    $i++; 
    if ($i > 20000){
	break;
    }
}



include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(650,500,"example1");
$graph->SetScale("textlin");
$graph->img->SetMargin(60,10,30,140);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTicks(30);
$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->Set(.00005,.00001);
$graph->yaxis->scale->ticks->SetPrecision(4);
$graph->title->Set("MM5 Forecasted Temps for Ames");
$graph->legend->Pos(0.01,0.01);

$graph->title->SetFont(FF_VERDANA,FS_BOLD,16);
$graph->yaxis->SetTitle("Temperature [C]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid GMT Time");
$graph->xaxis->SetTitleMargin(105);
$graph->yaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Skin Temp");
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetLegend("Air T");
$lineplot2->SetColor("blue");

// Create the linear plot
$lineplot3=new LinePlot($ydata3);
$lineplot3->SetLegend("Dew Point");
$lineplot3->SetColor("black");


$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->Add($lineplot3);

// Display the graph
$graph->Stroke();
?>

