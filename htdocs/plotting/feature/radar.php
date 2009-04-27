<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$dbconn = iemdb('access');
include("$rootpath/include/mlib.php");

$radtimes = Array();
$n0r = Array();
$fc = file('ames.txt');
while (list ($line_num, $line) = each ($fc)) {
  $tokens = split (" ", $line);
  $radtimes[] = strtotime( $tokens[0] ." ". $tokens[1] ) - (5*3600);
  $v = floatval($tokens[3]);
  if ($v > 0){
   $n0r[] = $v;
  } else {
   $n0r[] = "";
  }
}

$sql = "SELECT valid, tmpf, dwpf, sknt, vsby, pday
  from current_log WHERE station = 'SAMI4' and valid > '2009-04-13 06:00' 
  and valid < '2009-04-13 13:00' and dwpf > -99 ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
$times = Array();
$dwpf = Array();
$tmpf = Array();
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = strtotime( $row["valid"] );
  $dwpf[] = $row["dwpf"];
  $tmpf[] = $row["tmpf"]  ;
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,40,50,85);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("Md h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->y2axis->SetTitleMargin(20);
//$graph->yaxis->SetColor("blue");
//$graph->yaxis->title->SetColor("blue");
$graph->y2axis->SetColor("red");
$graph->y2axis->title->SetColor("red");
$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Temperature [F]");
$graph->y2axis->SetTitle("Reflectivity [dBZ]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Ames SchoolNet + NEXRAD');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($dwpf, $times);
$lineplot->SetLegend("Dew Point");
$lineplot->SetColor("green");
$lineplot->SetWeight(3);
$graph->Add($lineplot);

$lineplot3=new LinePlot($tmpf, $times);
$lineplot3->SetLegend("Air Temp");
$lineplot3->SetColor("black");
$lineplot3->SetWeight(3);
$graph->Add($lineplot3);


// Create the linear plot
$lineplot2=new BarPlot($n0r,$radtimes);
$lineplot2->SetLegend("NEXRAD");
$lineplot2->SetFillColor("red");
$lineplot2->SetWidth(5);
$graph->AddY2($lineplot2);

// Display the graph
$graph->Stroke();
?>
