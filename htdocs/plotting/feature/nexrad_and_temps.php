<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$asos = iemdb('asos');
include("$rootpath/include/mlib.php");

$obtimes = Array();
$tmpf = Array();
$rs = pg_query($asos, "SELECT valid, tmpf from alldata WHERE station = 'AMW' and valid BETWEEN '2009-12-01' and '2010-02-01' ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $tmpf[] = $row["tmpf"];
  $obtimes[] = strtotime( substr($row["valid"],0,16) );
}

$radtimes = Array();
$n0r = Array();
$fc = file('jan2010_nexrad.txt');
while (list ($line_num, $line) = each ($fc)) {
  $tokens = split (" ", $line);
  $radtimes[] = strtotime( $tokens[0] ." ". $tokens[1] ) - (6*3600);
  $n0r[] = floatval($tokens[2]);
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(47,45,60,60);
$graph->SetColor("white");
$graph->SetMarginColor("white");

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitleMargin(30);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,14);
//$graph->xaxis->SetTitle("25 JAN                         26 JAN");

//$graph->yaxis->SetColor("red");
//$graph->yaxis->title->SetColor("red");
$graph->yaxis->SetTitleMargin(24);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,10);
$graph->yaxis->SetTitle("Areal Coverage Estimate [%]");

$graph->title->Set("Iowa Storm Systems");
$graph->subtitle->Set("coverage of 10+dBZ NEXRAD returns (Dec09-Jan10)");
$graph->title->SetFont(FF_ARIAL,FS_BOLD,14);

//$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->SetTitleMargin(34);
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->SetTitle("Mean Wind Speed [mph]");


  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.2,0.08, 'right', 'top');
//  $graph->legend->SetLineSpacing(10);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

// Create the linear plot
$lineplot=new LinePlot($n0r,$radtimes);
//$lineplot->SetLegend("10+ dBZ NEXRAD Coverage");
$lineplot->SetColor("blue");
$lineplot->SetFillColor("blue");
$lineplot->SetWeight(2);
$graph->Add($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($tmpf,$obtimes);
//$lineplot->SetLegend("10+ dBZ NEXRAD Coverage");
$lineplot2->SetColor("red");
$lineplot2->SetWeight(2);
$graph->AddY2($lineplot2);




// Display the graph
$graph->Stroke();
?>
