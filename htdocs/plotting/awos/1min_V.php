<?php
// 1 minute schoolnet data plotter
// Cool.....

require_once "../../../config/settings.inc.php";
include("../../../include/database.inc.php");
include("../../../include/network.php");
require_once "../../../include/forms.php";
$nt = new NetworkTable("AWOS");
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_line.php");
include ("../../../include/jpgraph/jpgraph_scatter.php");
include ("../../../include/jpgraph/jpgraph_led.php");

$station = isset($_GET["station"]) ? xssafe($_GET["station"]): "";
$year = get_int404("year", date("Y", time() - 86400));
$month = get_int404("month", date("m", time() - 86400));
$day = get_int404("day", date("d", time() - 86400));


  $myTime = strtotime($year."-".$month."-".$day);



  $titleDate = date("M d, Y", $myTime);
  $tableName = sprintf("t%s", date("Y_m", $myTime));
  $sqlDate = date("Y-m-d", $myTime);


$mph = array();
$drct = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;


/** Time to get data from database **/
$connection = iemdb("awos");
$rs = pg_prepare($connection, "SELECT", "SELECT " .
        "to_char(valid, 'HH24:MI') as tvalid, sknt, drct from " .
        "". $tableName ." WHERE station = $1 and " .
        "  date(valid) = $2 ORDER by tvalid");

$result = pg_execute($connection, "SELECT", Array($station, $sqlDate));

pg_close($connection);

if (pg_num_rows($result) == 0){
 $led = new DigitalLED74();
 $led->StrokeNumber('NO DATA FOR THIS DATE',LEDC_GREEN);
 die();
}

for( $p=0; $row = pg_fetch_array($result); $p++)  {
  $strDate = $sqlDate ." ". $row["tvalid"];
  $timestamp = strtotime($strDate );
#  echo $thisTime ."||";

  $thisMPH = $row["sknt"] * 1.15;
  $thisDRCT = $row["drct"];
  if ($thisMPH > 200 )  $thisMPH = " ";
  
  $shouldbe = intval( $start ) + 60 * $i;
 
#  echo  $i ." - ". $line_num ."-". $shouldbe ." - ". $timestamp ;
  
  // We are good, write data, increment i
  if ( $shouldbe == $timestamp ){
#    echo " EQUALS <br>";
    if ($i % 10 == 0){
      $drct[$i] = $thisDRCT;
    }else{
      $drct[$i] = "-199";
    }
    $mph[$i] = $thisMPH;
    $i++;
    continue;
  
  // Missed an ob, leave blank numbers, inc i
  } else if (($timestamp - $shouldbe) > 0) {
#    echo " TROUBLE <br>";
    $tester = $shouldbe + 60;
    while ($tester <= $timestamp ){
      $tester = $tester + 60 ;
      $drct[$i] = "";
      $mph[$i] = "";

      $i++;
      $missing++;
    }
    if ($i % 10 == 0){
      $drct[$i] = $thisDRCT;
    } else {
      $drct[$i] = "";
    }
    $mph[$i] = $thisMPH;
    $i++;
    continue;
    
    $p--;
  } else if (($timestamp - $shouldbe) < 0) {
#    echo "DUP <br>";
     $dups++;
    
  }

} // End of while

$xpre = array(0 => '12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM',
    '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM', 'Noon',
    '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM',
    '8 PM', '9 PM', '10 PM', '11 PM', 'Midnight');


for ($j=0; $j<24; $j++){
  $xlabel[$j*60] = $xpre[$j];
}




// Create the graph. These two calls are always required
$graph = new Graph(600,300,"example1");
$graph->SetScale("textlin",0, 360);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(55,40,55,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(60);
$graph->xaxis->SetLabelAngle(90);
$graph->title->Set($nt->table[$station]['name'] ." Time Series");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.07);

$graph->yaxis->scale->ticks->Set(90,15);

$graph->yaxis->SetColor("blue");
$graph->y2axis->SetColor("red");

$graph->title->SetFont(FF_FONT1,FS_BOLD,16);

$graph->yaxis->SetTitle("Wind Direction");
$graph->y2axis->SetTitle("Wind Speed [MPH]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
$graph->yaxis->SetTitleMargin(30);
//$graph->y2axis->SetTitleMargin(28);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($mph);
$graph->AddY2($lineplot);
$lineplot->SetLegend("5 second Wind Speed");
$lineplot->SetColor("red");

// Create the linear plot
$sp1=new ScatterPlot($drct);
$graph->Add($sp1);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);

// Box for error notations
$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
$t1->SetPos(0.4,0.95);
$t1->SetOrientation("h");
$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
$t1->SetColor("black");
$graph->AddText($t1);

$graph->Stroke();
