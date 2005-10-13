<?php
$ydata = array();
$xlabel= array();

// $fcontents = file('/home/akrherz/TFD.out');
//$fcontents = file('/home/mm5/frost/tfd.out');
$fcontents = file('tfd/tfd.2001122700');
$i = 0;
$j = 0;
$k = 0;
while (list ($line_num, $line) = each ($fcontents)) {
     $parts = preg_split ("/[\s,]+/", $line);
     if ( $parts[2] >= 0 ) {
	if ( $j % 60 == 0 ){
     	    $xlabel[$k] = $parts[0] ."_". $parts[1];
	    $k++;
     	}
	if ( $parts[2] > 0 ) {
        	$ydata[$j] = $parts[2];
	} else {
		$ydata[$j] = 0.000005;
	}
        $j++;
    }
    $i++; 
    if ($i > 20000){
	break;
    }
}



include ("../dev/jpgraph.php");
include ("../dev/jpgraph_line.php");


// Create the graph. These two calls are always required
$graph = new Graph(650,400,"example1");
//$graph->SetScale("textlin",0,.00150);
$graph->SetScale("textlin",0,.150);
$graph->img->SetMargin(60,10,30,100);
$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetTextTicks(60);
$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->Set(.00005,.00001);
$graph->yaxis->scale->ticks->Set(.005,.001);
$graph->yaxis->scale->ticks->SetPrecision(4);
$graph->title->Set("Frost Accumulation");
$graph->legend->Pos(0.01,0.01);

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);
$graph->yaxis->SetTitle("Frost Accumulation [mm]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid GMT Time");
$graph->xaxis->SetTitleMargin(68);
$graph->yaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);


// Create the linear plot
$lineplot=new LinePlot($ydata);
$lineplot->SetLegend("Frost Accumulation (mm)");
$lineplot->SetColor("red");

$graph->Add($lineplot);

// Display the graph
$graph->Stroke();
?>

