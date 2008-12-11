<?php 
include("../../config/settings.inc.php");
$TITLE = "IEM | COOP | Freezing Dates";
include("$rootpath/include/header.php");
include("$rootpath/include/database.inc.php"); 
include("$rootpath/include/network.php"); 
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;

$sortcol = isset($_GET["sortcol"]) ? $_GET["sortcol"]: "station";

?>

<b>Nav:</b> <a href="<?php echo $rooturl; ?>/COOP/">COOP</a> <b> > </b> Freezing Dates<p>

<h3 class="heading">Freezing Dates</h3>

<div class="text">
<p>Using the NWS COOP data archive, significant dates relating to fall are
extracted and presented on this page.  The specific dates are the first 
occurance of that temperature and may have occured again in subsequent 
years.

<br>The "Record Lows" columns show the first fall occurance of a low
temperature.  The "Average Lows" column shows when certain climatological
thresholds are surpassed in the fall.
</p>
<?
function aSortBySecondIndex($multiArray, $secondIndex) {
        while (list($firstIndex, ) = each($multiArray))
                $indexMap[$firstIndex] = $multiArray[$firstIndex][$secondIndex];
        asort($indexMap);
        while (list($firstIndex, ) = each($indexMap))
                if (is_numeric($firstIndex))
                        $sortedArray[] = $multiArray[$firstIndex];
                else $sortedArray[$firstIndex] = $multiArray[$firstIndex];
        return $sortedArray;
}
 

 $connection = iemdb("coop");

 $query = "select station, valid, min_low, min_low_yr from climate 
     WHERE valid > '2000-08-01' and min_low <= 32 
     and station NOT IN ('ia4381', 'ia7842') ORDER by valid";
 $rs = pg_exec($connection, $query);

 $query = "select station, valid, low from climate 
     WHERE valid > '2000-08-01' and low <= 40 
     and station NOT IN ('ia4381', 'ia7842') ORDER by valid";
 $rs2 = pg_exec($connection, $query);


 $data = Array();
 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
 {
   $st = $row["station"];
   if (! isset($data[$st])){
     $data[$st] = Array("min_low" => 100, "station" => $st);
     $data[$st]["low"] = $row["min_low"];
     $data[$st]["lowyr"] = $row["min_low_yr"] ."-". substr($row["valid"], 5, 6);
   }
   if (! isset($data[$st]["low28"]) ){
     if (intval($row["min_low"]) < 29 ){
       $data[$st]["low28"] = $row["min_low"];
       $data[$st]["low28yr"] = $row["min_low_yr"] ."-". substr($row["valid"], 5, 6);
     }
   }
 
 }

 for( $i=0; $row = @pg_fetch_array($rs2,$i); $i++)
 {
   $st = $row["station"];
   if (! isset($data[$st]["avelow40day"])){
     if ( intval($row["low"]) < 41 ){
       $data[$st]["avelow40day"] = substr($row["valid"], 5, 6);
     }
   }
   if (! isset($data[$st]["avelow32day"])){
     if ( intval($row["low"]) < 33 ){
       $data[$st]["avelow32day"] = substr($row["valid"], 5, 6);
     }
   }
   if (! isset($data[$st]["avelow28day"])){
     if ( intval($row["low"]) < 28 ){
       $data[$st]["avelow28day"] = substr($row["valid"], 5, 6);
     }
   }

 }

 $finalA = Array();
 $finalA = aSortBySecondIndex($data, $sortcol);

 //-------------------------------------------------

 echo "<table border=1 cellpadding=2>
  <tr>
    <th rowspan='3'><a href='freezing.php?sortcol=station'>COOP Site:</a></th>
    <th colspan='4'>Record Lows:</th>
    <th colspan='3'>Average Lows:</th>
  </tr>
  <tr>
    <th colspan='2'>Temp <= 32&deg;F</th>
    <th colspan='2'>Temp <= 28&deg;F</th>
    <td rowspan='2'><a href='freezing.php?sortcol=avelow40day'>Below 40&deg;F</a></td>
    <td rowspan='2'><a href='freezing.php?sortcol=avelow32day'>Below 32&deg;F</a></td>
    <td rowspan='2'><a href='freezing.php?sortcol=avelow28day'>Below 28&deg;F</a></td>
  </tr>
    <td>Temp:</td>
    <td><a href='freezing.php?sortcol=lowyr'>Date:</a></td>
    <td>Temp:</td>
    <td><a href='freezing.php?sortcol=low28yr'>Date:</a></td>
  </tr>";

 foreach($finalA as $key => $value ){
   echo "<tr><td>". $cities[strtoupper($key)]["name"] ."</td>
    <td>". $data[$key]["low"] ."</td>
    <td>". $data[$key]["lowyr"] ."</td>
    <td>". $data[$key]["low28"] ."</td>
    <td>". $data[$key]["low28yr"] ."</td>
    <td>". $data[$key]["avelow40day"] ."</td>
    <td>". $data[$key]["avelow32day"] ."</td>
    <td>". $data[$key]["avelow28day"] ."</td>
    </tr>\n";
 }

 echo "</table>\n";
 pg_close($connection);
?></div>
<?php include("$rootpath/include/footer.php"); ?>
