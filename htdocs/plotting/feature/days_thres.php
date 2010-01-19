<?php
set_time_limit(1800);
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$pgconn = iemdb('coop');

$data = Array();

$rs = pg_query($pgconn, "SELECT year, day, low from alldata 
      WHERE stationid = 'ia0200' and low < 51 and month > 6 
      ORDER by day ASC");
$lastyear = 0;
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $year = $row["year"];
  $ob = $row["low"];
  if ($year == $lastyear){ continue; }
  if ($ob < 33){ $lastyear = $year; continue; }
  if (! array_key_exists($year, $data)){ $data[$year] = Array(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0); }

  for($j=50;$j>=$ob;$j--){
    $data[$year][50 - $j] += 1;
  }
}

$cnt = sizeof($data);
$sum_days = Array(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
$max_days = Array(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
$min_days = Array(100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100,100);
for ($year=1893;$year<2009;$year++){
  for ($i=50;$i>32;$i--){
    $sum_days[50 - $i] += $data[$year][50 - $i];
    if ($data[$year][50 - $i] > $max_days[50 - $i]){ 
      $max_days[50 - $i] = $data[$year][50 - $i];
    }
    if ($data[$year][50 - $i] < $min_days[50 - $i]){ 
      $min_days[50 - $i] = $data[$year][50 - $i];
    }
  }
}

$avg_days = Array(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
for ($i=50;$i>32;$i--){
  $avg_days[50 - $i] = $sum_days[50 - $i] / $cnt;
}

$d2009 = Array(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);
$pgconn = iemdb('access');
$rs = pg_query($pgconn, "SELECT min_tmpf from summary WHERE day > '2009-06-01'
      and station = 'AMW' and min_tmpf < 51");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $ob = $row["min_tmpf"];
  for($j=50;$j>=$ob;$j--){
    $d2009[50 - $j] += 1;
  }
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,400,"example1");
$graph->SetScale("textlin");
//$graph->SetY2Scale("lin",-55,75);

//$graph->SetBackgroundGradient('white','green',GRAD_HOR,BGRAD_PLOT);
$graph->SetMarginColor('white');
//$graph->SetColor('white');
//$graph->SetBackgroundGradient('navy','white',GRAD_HOR,BGRAD_MARGIN);
$graph->SetFrame(true,'white');

$graph->ygrid->Show();
$graph->xgrid->Show();
$graph->ygrid->SetColor('gray@0.5');
$graph->xgrid->SetColor('gray@0.5');

$graph->img->SetMargin(40,5,25,50);

$graph->xaxis->SetTickLabels( Array(50,49,48,47,46,45,44,43,42,41,40,39,38,37,36,35,34,33) );
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(10);
$graph->xaxis->SetTitleMargin(20);

$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->xaxis->SetTitle("Low Temperature Threshold");
$graph->yaxis->SetTitle("Number of Days ");
//$graph->y2axis->SetTitle("Temperature [F]");

$graph->title->Set("Number of Days At-Or-Below a Low Temp\nbefore First Fall 32 °F Ames [1893-2008]");
$graph->title->SetFont(FF_ARIAL,FS_BOLD,12);

$graph->legend->SetLayout(LEGEND_VERT);
$graph->legend->SetPos(0.0,0.3, 'right', 'top');
//$graph->legend->SetLineSpacing(3);

/*
$bp1=new BarPlot($max_days);
$bp1->SetFillColor("red");
$graph->Add($bp1);

$bp2=new BarPlot($avg_days);
$bp2->SetFillColor("blue");
$graph->Add($bp2);

$bp3=new BarPlot($min_days);
$bp3->SetFillColor("white");
$graph->Add($bp3);
*/

// Create the linear plot
$sp1=new ScatterPlot($avg_days);
$sp1->SetLegend("Average");
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetType(MARK_FILLEDCIRCLE);

// Create the linear plot
$sp2=new ScatterPlot($max_days);
$sp2->SetLegend("Maximum");
$sp2->mark->SetFillColor("red");
$sp2->mark->SetType(MARK_FILLEDCIRCLE);

$sp3=new ScatterPlot($min_days);
$sp3->SetLegend("Minimum");
$sp3->mark->SetFillColor("yellow");
$sp3->mark->SetType(MARK_FILLEDCIRCLE);

$sp4=new ScatterPlot($d2009);
$sp4->SetLegend("2009");
$sp4->mark->SetFillColor("black");
$sp4->mark->SetType(MARK_UTRIANGLE);

$graph->Add($sp2);
$graph->Add($sp1);
$graph->Add($sp3);
$graph->Add($sp4);


// Display the graph
$graph->Stroke();
?>
