<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$postgis = iemdb('postgis');
$snet = iemdb('snet');
$access = iemdb('access');
include("$rootpath/include/mlib.php");

/* Road is either closed 86 or travel not advised 51 */
$rs = pg_query($postgis, "select valid, 
  sum(case when cond_code in (86,51) then 1 else 0 end) as total 
  from roads_2009_log WHERE 
  valid BETWEEN '2009-12-08' and '2009-12-11' 
  GROUP by valid ORDER by valid ASC");
$roads = Array();
$rtimes = Array();
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $roads[] = $row["total"] / 240.0 * 100;
  $rtimes[] = strtotime( $row["valid"] );
}

/* Average winds, via schoolnet? 
$rs = pg_query($snet, "select valid, avg(sknt) as wind from t2009_12 
  WHERE valid BETWEEN '2009-12-08' and '2009-12-11' and 
  sknt >= 0 GROUP by valid ORDER by valid ASC");
$wind = Array();
$wtimes = Array();
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $wind[] = $row["wind"] * 1.14;
  $wtimes[] = strtotime( $row["valid"] );
} */

/* Average winds, via schoolnet? */
$rs = pg_query($access, "select valid, avg(sknt) as wind from current_log
  WHERE valid BETWEEN '2009-12-08' and '2009-12-11' and 
  network in ('IA_ASOS','AWOS') GROUP by valid ORDER by valid ASC");
$wind = Array();
$wtimes = Array();
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $wind[] = $row["wind"] * 1.14;
  $wtimes[] = strtotime( $row["valid"] );
}

/* We need to filter the wind data */
$newwind = Array();
$newwtimes = Array();
for($i=5;$i<sizeof($wind)-5;$i++){
  $newwind[] = ($wind[$i-5] + $wind[$i-4] + $wind[$i-3] +$wind[$i-2] +$wind[$i-1] + $wind[$i] + $wind[$i+4] + $wind[$i+3] +$wind[$i+2] +$wind[$i+1]) / 10.0;
  $newwtimes[] = $wtimes[$i];
}

$radtimes = Array();
$n0r = Array();
$fc = file('blizzard.txt');
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
$graph->img->SetMargin(47,45,40,60);
$graph->SetColor("white");
$graph->SetMarginColor("white");

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTitleMargin(35);
//$graph->xaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
//$graph->xaxis->SetTitle("8 ");

//$graph->yaxis->SetColor("red");
//$graph->yaxis->title->SetColor("red");
$graph->yaxis->SetTitleMargin(24);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->yaxis->SetTitle("Areal Coverage Estimate [%]");

$graph->title->Set("Iowa's Blizzard 8-10 Dec 2009");
$graph->title->SetFont(FF_ARIAL,FS_BOLD,14);

$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->y2axis->SetColor("blue");
$graph->y2axis->SetTitleMargin(34);
$graph->y2axis->title->SetColor("blue");
$graph->y2axis->SetTitle("Mean Wind Speed [mph]");


  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.1,0.1, 'right', 'top');
//  $graph->legend->SetLineSpacing(10);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

$l = new LinePlot($roads, $rtimes);
$l->SetLegend("Closed/Travel Advisory Roads");
$l->SetColor("red");
$l->SetWeight(2);
$graph->Add($l);

// Create the linear plot
$lineplot3=new LinePlot($newwind,$newwtimes);
//$lineplot2->SetLegend("NEXRAD");
$lineplot3->SetColor("blue");
$lineplot3->SetWeight(2);
$graph->AddY2($lineplot3);

// Create the linear plot
$lineplot2=new LinePlot($n0r,$radtimes);
$lineplot2->SetLegend("10+ dBZ NEXRAD Coverage");
$lineplot2->SetColor("green");
$lineplot2->SetWeight(2);
$graph->Add($lineplot2);





// Display the graph
$graph->Stroke();
?>
