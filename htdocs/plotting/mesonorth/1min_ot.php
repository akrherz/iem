<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
require_once "../../../include/jpgraph/jpgraph_led.php";

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");

$myTime = mktime(0,0,0,$month,$day,$year);

$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);

$fp = "/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0003.dat";
if (! file_exists($fp))
{
 $led = new DigitalLED74();
 $led->StrokeNumber('NO DATA FOR THIS DATE',LEDC_GREEN);
 die();

}
$fcontents = file($fp);

$oldformat = 1;
if ($myTime >= mktime(0,0,0,8,12,2005))
{
  $oldformat = 0;
}

$t1 = array();
$t2 = array();
$t3 = array();
$t4 = array();
$times = array();

$start = intval( $myTime );
$i = 0;

$new_contents = array_slice($fcontents,2);
foreach($new_contents as $line_num => $line)
{
  $parts = preg_split ("/,/", $line); 
  if (sizeof($parts) < 3) continue;
  $hhmm = str_pad($parts[3],4,"0",STR_PAD_LEFT);
  $hh = substr($hhmm,0,2);
  if ($hh == 24){$hh = 00;}
  $mm = substr($hhmm,2,3);
  $timestamp = mktime($hh,$mm,0,$month,$day,$year);
  if ($oldformat)
  {
    $thisTmpc = $parts[10];
    $t1[] = round ((9.0/5.0*$thisTmpc)+32.0,2);
  }
  else
  {
    $t1[] = $parts[4];
    $t2[] = $parts[5];
    $t3[] = $parts[6];
    $t4[] = $parts[7];
  }
  $times[] = $timestamp;

} // End of while




// Create the graph. These two calls are always required
$graph = new Graph(1200, 628);
$graph->SetScale("datlin");

$graph->img->SetMargin(65,20,45,90);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
//$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(6);
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->scale->SetDateFormat("h A");
$graph->xaxis->SetLabelFormatString("h:i A", true);

//$graph->yaxis->scale->ticks->SetPrecision(1);
//$graph->yaxis->scale->ticks->Set(1.2,0.5);

$graph->yscale->SetGrace(10);
$graph->title->Set("Cluster Room Temperature ($titleDate)");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.05);

//[DMF]$graph->y2axis->scale->ticks->Set(100,25);
//[DMF]$graph->y2axis->scale->ticks->SetPrecision(0);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time (Central US)");
$graph->xaxis->SetTitleMargin(55);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

$sensors = Array("Out of Subfloor", "Inbound Top", "Outbound Top", "Room");
if ($myTime > mktime(0,0,0,7,9,2006))
  $sensors = Array("In Air Handler", "Out Air Handler", "Out Floor", "Room");
if ($myTime > mktime(0,0,0,2,29,2012))
  $sensors = Array("In Air Handler", "Out Air Handler", "Out Rack", "In Rack");
  
// Create the linear plot
$lineplot=new LinePlot($t1, $times);
if (sizeof($t2) > 0) {
  $lineplot->SetLegend($sensors[0]);
} else {
  $lineplot->SetLegend("Room Temp");
}
$lineplot->SetColor("red");
$lineplot->SetWeight(2);
$graph->Add($lineplot);

if (sizeof($t2) > 0) {
// Create the linear plot
$lineplot2=new LinePlot($t2, $times);
$lineplot2->SetLegend($sensors[1]);
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(2);
$graph->Add($lineplot2);

// Create the linear plot
$lineplot3=new LinePlot($t3, $times);
$lineplot3->SetLegend($sensors[2]);
$lineplot3->SetColor("green");
$lineplot3->SetWeight(2);
$graph->Add($lineplot3);

// Create the linear plot
$lineplot4=new LinePlot($t4, $times);
$lineplot4->SetLegend($sensors[3]);
$lineplot4->SetColor("black");
$lineplot4->SetWeight(2);
$graph->Add($lineplot4);
}

$graph->Stroke();

?>
