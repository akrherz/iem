<?php
 // precScat.php
 //  Plots scatter plots of precip values...

 $c = pg_connect("mesonet.agron.iastate.edu", 5432, "postgis");
 $q =  "SELECT n.valid, n.station, round(CASE WHEN n.p01i < 0 
   THEN 0 ELSE n.p01i END, 2)
   as n_p01i, round(h.p01i,2) as h_p01i from nex_2002 n LEFT JOIN hp_2002 h 
   using (valid, station) WHERE (n.p01i > 0 and h.p01i > 0)";

 $rs = pg_exec($c, $q);

 $nex = Array();
 $obs = Array();

 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) 
 { 
   $nex[] = $row["n_p01i"];
   $obs[] = $row["h_p01i"];
 }

 $m = max($nex);
 if (max($obs) > $m)  $m = max($obs);

 $l = Array();

 $l[0] = 0;
 $l[1] = 1;
 $l[2] = 2;
 $l[3] = 3;
 $l[4] = 4;

 pg_close($c);

 include ("../dev19/jpgraph.php");
 include ("../dev19/jpgraph_line.php");
 include ("../dev19/jpgraph_scatter.php");

$graph = new Graph(640,480,"example1");
$graph->SetScale("lin");
$graph->img->SetMargin(40,10,35,40);
//$graph->xaxis->SetFont(FS_FONT1,FS_BOLD);

$graph->xaxis->SetLabelAngle(90);
$graph->title->Set("Both Wet ScatterPlot");
$graph->subtitle->Set("Both Greater Than Zero");

$graph->title->SetFont(FF_FONT1,FS_BOLD,10);
$graph->yaxis->SetTitle("Observed");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,10);
$graph->yaxis->SetTitleMargin(30);
$graph->xaxis->SetTitle("NEXRAD Estimate");
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,10);
$graph->xaxis->SetTitleMargin(10);
$graph->xaxis->SetPos("min");

$graph->legend->Pos(0.6, 0.1);
$graph->legend->SetLayout(LEGEND_HOR);

// Create the linear plot
$sp=new ScatterPlot($obs, $nex);
$sp->mark->SetWidth(3);
$sp->mark->SetType(MARK_FILLEDCIRCLE);
$sp->mark->SetFillColor("navy");

$l1=new LinePlot($l);
//$l1->SetSize(2);
$l1->SetColor("red");


$graph->Add($sp);
$graph->Add($l1);

$graph->Stroke("/mesonet/www/html/tmp/positive.png");

?>
<img src="/tmp/positive.png">
