<?php
$ydata1_mm5 = array();

$ydata1_ssi = array();

$xlabel= array();

if (strlen($varnum) == 0){
  $varnum = 4;
}

$varnames = Array("Skin Temp", "Air Temp", "Dew Point", "Wind Spd");
$varunits = Array("F", "F", "F", "MPH");
$varname1 = $varnames[$varnum - 4];
$varname2 = $varnames[$varnum - 4];
$varunit = $varunits[$varnum - 4];
if ($varnum == 4){
  $varname1 = "Skin Temp";
  $varname2 = "Pavement Temp";
}


$fcontents_mm5 = file('/home/mm5/frost/fort.201');
$fcontents_ssi = file('/home/mesonet/SSI/frost/fort.201');

$i = 0;
$k = 0;
while (list ($line_num, $line) = each ($fcontents_mm5)) {
     $parts = preg_split ("/[\s,]+/", $line);
     if ($i == 0){
     	$startVal = $parts[1];
     }
     if ( $i % 120 == 0 ){
	    $xlabel[$k] = $parts[2] ." ". $parts[3];
//    	    $xlabel[$k] = $parts[1];
	    $k++;
     }
     $ydata1_mm5[$i] = $parts[$varnum];
    $i++; 
    if ($i > 20000){
	break;
    }
}

$i = 0;
$offset = 0;
while (list ($line_num, $line) = each ($fcontents_ssi)) {
     $parts = preg_split ("/[\s,]+/", $line);
     $minVal = $parts[1] + 360;
     if ($i == 0){
     	$offset = $minVal - $startVal;
     }
 
     $ydata1_ssi[$i+$offset] = $parts[$varnum];
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
$graph->xaxis->SetTextTicks(120);
$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->Set(.00005,.00001);
$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->title->Set("MM5 vs SSI Forecast for Ames");
$graph->legend->Pos(0.01,0.01);

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle($varname ." [". $varunit ."]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid GMT Time");
$graph->xaxis->SetTitleMargin(105);
$graph->yaxis->SetTitleMargin(48);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($ydata1_mm5);
$lineplot->SetLegend("MM5 ".$varname1 );
$lineplot->SetColor("red");

// Create the linear plot
$lineplot2=new LinePlot($ydata1_ssi);
$lineplot2->SetLegend("SSI ".$varname2 );
$lineplot2->SetColor("blue");

$graph->Add($lineplot);
$graph->Add($lineplot2);

// Display the graph
$graph->Stroke();
?>

