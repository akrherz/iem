<?php
// 1 minute schoolnet data plotter
// Cool.....

include("../../../config/settings.inc.php");


include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable(Array("IA_ASOS","NE_ASOS","IL_ASOS","SD_ASOS"));
$cities = $nt->table;
include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_led.php");

$station = isset($_GET["station"]) ? $_GET["station"] : "DSM";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"]: date("d");


  $myTime = strtotime($year."-".$month."-".$day);



$titleDate = strftime("%b %d, %Y", $myTime);
$tableName = strftime("t%Y_1minute", $myTime);
$sqlDate = strftime("%Y-%m-%d", $myTime);


$mph = array();
$drct = array();
$xlabel = array();

$start = intval( $myTime );
$i = 0;

$dups = 0;
$missing = 0;


/** Time to get data from database **/
$connection = iemdb("asos");
$query = "SELECT to_char(valid, 'HH24:MI') as tvalid, sknt, drct from 
  ". $tableName ." WHERE station = '". $station ."' and 
  date(valid) = '". $sqlDate ."' ORDER by tvalid";

$result = pg_exec($connection, $query);

pg_close($connection);
if (pg_num_rows($result) == 0){
 $led = new DigitalLED74();
 $led->StrokeNumber('NO DATA FOR THIS DATE',LEDC_GREEN);
 die();
}

for( $p=0; $row = @pg_fetch_array($result,$p); $p++)  {
  $strDate = $sqlDate ." ". $row["tvalid"];
  $timestamp = strtotime($strDate );
#  echo $thisTime ."||";

  $thisMPH = $row["sknt"] * 1.15;
  $thisDRCT = $row["drct"];
  if ($thisMPH > 200 )  $thisMPH = "";
  
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
      $drct[$i] = "-199";
      $mph[$i] = "";

      $i++;
      $missing++;
    }
    if ($i % 10 == 0){
      $drct[$i] = $thisDRCT;
    } else {
      $drct[$i] = "-199";
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
$graph->title->Set($cities[$station]['name'] ." Time Series");
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
$lineplot->SetLegend("5 second Wind Speed");
$lineplot->SetColor("red");

// Create the linear plot
$sp1=new ScatterPlot($drct);
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


$graph->Add($sp1);
$graph->AddY2($lineplot);
$graph->Stroke();
?>
