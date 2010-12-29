<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$asos = iemdb('asos');
$rwis = iemdb('rwis');
include("$rootpath/include/mlib.php");


$wobtimes = Array();
$winds = Array();
$rs = pg_query($asos, "SELECT valid, sknt from t2010 WHERE station = 'HNR' " .
		"and valid BETWEEN '2010-12-11' and '2010-12-13' and sknt >= 0 " .
		"ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $winds[] = $row["sknt"] * 1.15;
  $wobtimes[] = strtotime( substr($row["valid"],0,16) );
}


$obtimes = Array();
$sped = Array();
$rs = pg_query($rwis, "select valid, avg_speed, normal_vol from t2010_traffic " .
		"where station = 'RDAI4' and lane_id = 3 and valid > '2010-12-11' " .
		"and valid < '2010-12-13'  ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  
  $obtimes[] = strtotime( substr($row["valid"],0,16) );
  if ($row["normal_vol"] > 0){ 
  	$sped[] = $row["avg_speed"];
  } else {
  	$sped[] = '';
  }
}

$radtimes = Array();
$n0r = Array();
$fc = file('adair.txt');
while (list ($line_num, $line) = each ($fc)) {
  $tokens = split (" ", $line);
  $radtimes[] = strtotime( $tokens[0] ." ". $tokens[1] ) - (6*3600);
  if (floatval($tokens[3]) > 0){ 
  $n0r[] = floatval($tokens[3]);
  } else {
  	$n0r[] = 0;
  }
  
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,320,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin", 0, 40);
$graph->img->SetMargin(47,45,60,110);
$graph->SetColor("white");
$graph->SetMarginColor("white");

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTitleMargin(30);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD,8);
$graph->yaxis->SetTitle("Wind or Traffic Speed [mph]");

//$graph->yaxis->SetColor("red");
//$graph->yaxis->title->SetColor("red");
$graph->yaxis->SetTitleMargin(24);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,10);
$graph->y2axis->SetTitle("NEXRAD Reflectivity [dBZ]");

$graph->title->Set("11-12 Dec 2010: Adair RWIS sensor on I-80");
$graph->subtitle->Set("traffic speed, wind speed, and NEXRAD Reflectivity");
$graph->title->SetFont(FF_ARIAL,FS_BOLD,11);

//$graph->y2axis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->y2axis->SetColor("blue");
//$graph->y2axis->SetTitleMargin(34);
$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->SetTitle("Mean Wind Speed [mph]");


//  $graph->legend->SetLayout(LEGEND_VERT);
  $graph->legend->SetPos(0.2,0.12, 'right', 'top');
//  $graph->legend->SetLineSpacing(10);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

// Create the linear plot
$lineplot2=new LinePlot($sped,$obtimes);
$graph->Add($lineplot2);
$lineplot2->SetLegend("Traffic Speed");
$lineplot2->SetColor("red");
$lineplot2->SetWeight(2);

// Create the linear plot
$lineplot3=new LinePlot($winds,$wobtimes);
$graph->Add($lineplot3);
$lineplot3->SetLegend("Wind Speed");
$lineplot3->SetColor("green");
$lineplot3->SetWeight(2);

// Create the linear plot
$lineplot=new LinePlot($n0r,$radtimes);
$graph->AddY2($lineplot);
//$lineplot->SetLegend("10+ dBZ NEXRAD Coverage");
$lineplot->SetColor("blue");
$lineplot->SetFillColor("blue");
$lineplot->SetWeight(2);





// Display the graph
$graph->Stroke();
?>
