<?php
include_once("../../../config/settings.inc.php");
include_once("$rootpath/include/snet_locs.php");
include_once("$rootpath/include/mlib.php");
include_once("$rootpath/include/database.inc.php");

$meta = $cities[strtoupper($tv)][$station];

$year = isset( $_GET["year"] ) ? $_GET["year"] : date("Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("d");
$myTime = mktime(0,0,0,$month,$day,$year);
$today = mktime(0,0,0,date("m"), date("d"), date("Y"));


if ($myTime == $today)
{
  /* Look in IEM Access! */
  $dbconn = iemdb("access");
  $tbl = "current_log";
  $pcol = ", pres as alti";
} else 
{
/* Dig in the archive for our data! */
  $dbconn = iemdb("snet");
  $tbl = sprintf("t%s", date("Y_m", $myTime) );
  $pcol = "";
}
$rs = pg_prepare($dbconn, "SELECT", "SELECT * $pcol from $tbl 
                 WHERE station = $1 and date(valid) = $2 ORDER by valid ASC");
$rs = pg_execute($dbconn, "SELECT", Array($station, date("Y-m-d", $myTime)));
if (pg_num_rows($rs) == 0) { 

  echo "<br /><p><h3>No observations found for this date, sorry</h3>";
  return;
}

$imgwidth = 640;
$imgheight = 480;

$dirRef = strftime("%Y_%m/%d", $myTime);
$matchDate = strftime("%m/%d/%y", $myTime);

$titleDate = strftime("%b %d, %Y", $myTime);
$href = strftime("/tmp/".$station."_%Y_%m_%d", $myTime);

$wA = mktime(0,0,0, 8, 4, 2002);
$wLabel = "1min avg Wind Speed";
if ($wA > $myTime){
 $wLabel = "Instant Wind Speed";
}


// BUILD Arrays to hold minute-by-minute data
$tmpf = Array();
$dwpf = Array();
$sr = Array();
$mph = array();
$drct = array();
$gust = array();
$prec = array();
$alti = array();
$times = Array();

for($i=0;$row = @pg_fetch_array($rs,$i); $i++)
{
  $ts = strtotime( substr($row["valid"],0,16) );
  $times[] = $ts;

  $thisTmpf = $row["tmpf"];
  $thisRelH = $row["relh"];
  $thisSR = $row["srad"];
  $thisMPH = $row["sknt"] * 1.15;
  if ($thisMPH < 0) $thisMPH = 0;
  $thisDRCT = $row["drct"];
  if ($thisDRCT < 0) $thisDRCT = 0;
  $thisGust = $row["gust"] * 1.15;
  if ($thisGust < 0) $thisGust = 0;
  $thisALTI = $row["alti"];
  $thisPREC = $row["pday"];
  if ($thisRelH > 0){
    $thisDwpf = dwpf($thisTmpf, $thisRelH);
  } else {
    $thisDwpf = "";
  }
  if ($thisTmpf < -50 || $thisTmpf > 150 ){
    $thisTmpf = "";
  }
  if ($thisDwpf < -50 || $thisDwpf > 150 ){
    $thisDwpf = "";
  }
 
  $tmpf[] = $thisTmpf;
  $dwpf[] = $thisDwpf;

  if ($thisSR >= 0) $sr[] = $thisSR;
  else $sr[] = "";

  if ($i % 10 == 0){
    $drct[] = $thisDRCT;
  }else{
    $drct[] = "-199";
  }
  $mph[] = $thisMPH;
  $gust[] = $thisGust;
  $prec[] = $thisPREC;
  $alti[] = $thisALTI * 33.8639;
  if ($alti[$i] < 900)   $alti[$i] = "";

} // End of while


$cityname = $meta['city'];

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


function common_graph($graph)
{
  $tcolor = array(230,230,0);
  /* Common for all our plots */
  $graph->img->SetMargin(80,60,40,80);
  //$graph->img->SetAntiAliasing();
  $graph->xaxis->SetTextTickInterval(120);
  $graph->xaxis->SetPos("min");

  $graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,14);
  $graph->xaxis->SetFont(FF_FONT1,FS_BOLD,12);
  //$graph->xaxis->title->SetBox( array(150,150,150), $tcolor, true);
  //$graph->xaxis->title->SetColor( $tcolor );
  $graph->xaxis->SetTitleMargin(15);
  $graph->xaxis->SetLabelFormatString("h A", true);
  $graph->xaxis->SetLabelAngle(90);
  $graph->xaxis->SetTitleMargin(50);

  $graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,14);
  $graph->yaxis->SetFont(FF_FONT1,FS_BOLD,12);
  //$graph->yaxis->title->SetBox( array(150,150,150), $tcolor, true);
  //$graph->yaxis->title->SetColor( $tcolor );
  $graph->yaxis->SetTitleMargin(50);
  $graph->yscale->SetGrace(10);

  $graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,14);
  $graph->y2axis->SetFont(FF_FONT1,FS_BOLD,12);
  //$graph->y2axis->title->SetBox( array(150,150,150), $tcolor, true);
  //$graph->y2axis->title->SetColor( $tcolor );
  $graph->y2axis->SetTitleMargin(40);

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.94, 'left', 'top');
  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

  return $graph;
}

// Create the graph. These two calls are always required
$graph = new Graph($imgwidth,$imgheight,"example1");

$graph->SetScale("datelin", min($dwpf)-5, max($tmpf)+5);
$graph->SetY2Scale("lin", 0, 1200);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Temperature [F]");
$graph->y2axis->SetTitle("Solar Radiation [W m**-2]", "low");
$graph->tabtitle->Set(' '. $cityname ." on ". $titleDate .' ');

$graph = common_graph($graph);

/* Custom */
$graph->yaxis->scale->ticks->SetLabelFormat("%5.1f");
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");



$graph->y2axis->scale->ticks->Set(100,25);
$graph->y2axis->scale->ticks->SetLabelFormat("%-4.0f");


// Create the linear plot
$lineplot=new LinePlot($tmpf, $times);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");
//$lineplot->SetWeight(2);
// Create the linear plot

$lineplot2=new LinePlot($dwpf, $times);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");
//$lineplot2->SetWeight(2);

// Create the linear plot
$lineplot3=new LinePlot($sr, $times);
$lineplot3->SetLegend("Solar Rad");
$lineplot3->SetColor("black");
//$lineplot3->SetWeight(2);

$graph->Add($lineplot2);
$graph->Add($lineplot);
$graph->AddY2($lineplot3);

$graph->Stroke("/mesonet/www/html/".$href."_1.png");

echo '<p><img src="'.$href.'_1.png">';

//__________________________________________________________________________

// Create the graph. These two calls are always required
$graph = new Graph($imgwidth,$imgheight,"example1");

$graph->SetScale("datelin",0, 360);
$graph->SetY2Scale("lin");
$graph->y2axis->SetColor("red");
$graph->y2axis->SetTitle("Wind Speed [MPH]");
$graph->xaxis->SetTitle("Valid Local Time");
$graph->tabtitle->Set(' '. $cityname ." on ". $titleDate .' ');

$graph = common_graph($graph);

$graph->yaxis->scale->ticks->SetLabelFormat("%5.1f");
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->yaxis->SetColor("blue");
$graph->yaxis->SetTitle("Wind Direction [N=0, E=90, S=180, W=270]");

// Create the linear plot
$lineplot=new LinePlot($mph, $times);
$lineplot->SetLegend($wLabel);
$lineplot->SetColor("red");

$lp1=new LinePlot($gust, $times);
$lp1->SetLegend("Peak Wind Gust");
$lp1->SetColor("black");

// Create the linear plot
$sp1=new ScatterPlot($drct, $times);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);
$sp1->SetLegend("Wind Direction");

$graph->Add($sp1);
$graph->AddY2($lineplot);
$graph->AddY2($lp1);

$graph->Stroke("/mesonet/www/html/".$href."_2.png");
echo '<p><img src="'.$href.'_2.png">';

//__________________________________________________________________________
$graph = new Graph($imgwidth,$imgheight);
$graph->SetScale("datelin");
$graph->SetY2Scale("lin",0, intval((max($prec)+1)));

$graph->tabtitle->Set(' '. $cityname ." on ". $titleDate .' ');
$graph->xaxis->SetTitle("Valid Local Time");
$graph->y2axis->SetTitle("Accumulated Precipitation [inches]");
$graph->yaxis->SetTitle("Pressure [millibars]");

$graph = common_graph($graph);

$graph->yaxis->SetTitleMargin(60);

$graph->y2axis->scale->ticks->Set(0.5,0.25);
$graph->y2axis->scale->ticks->SetLabelFormat("%4.2f");
$graph->y2axis->SetColor("blue");

$graph->yaxis->scale->ticks->SetLabelFormat("%4.1f");
$graph->yaxis->scale->ticks->Set(1,0.1);
$graph->yaxis->SetColor("black");
$graph->yscale->SetGrace(10);
//$graph->yscale->SetAutoTicks();

// Create the linear plot
$lineplot=new LinePlot($alti, $times);
$lineplot->SetLegend("Pressure");
$lineplot->SetColor("black");
//$lineplot->SetWeight(2);

// Create the linear plot
$lineplot2=new LinePlot($prec, $times);
$lineplot2->SetLegend("Precipitation");
$lineplot2->SetFillColor("blue@0.1");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(2);
//$lineplot2->SetFilled();
//$lineplot2->SetFillColor("blue");

// Box for error notations
//$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//$t1->SetPos(0.4,0.95);
//$t1->SetOrientation("h");
//$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//$t1->SetColor("black");
//$graph->AddText($t1);

$graph->AddY2($lineplot2);
$graph->Add($lineplot);

$graph->Stroke("/mesonet/www/html/".$href."_3.png");
echo '<p><img src="'.$href.'_3.png">';

?>
