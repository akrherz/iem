<html>
<head>
 <title>IEM | GIS | County NEXRAD</title>
</head>
<body bgcolor="#EEEEEE">

<table bgcolor="black" cellspacing="0">
<tr>
 <td>

<?php
// county.php  - County based NEXRAD!!!
//               I know, I know


$extents = Array("DMX" => Array(1270178, 863000, 1755341, 1276783),
  "FSD" => Array(540178, -34000, 800341, 450783),
  "ARX" => Array(760178, -30000, 900341, 450783),
  "DVN" => Array(450000, 350000, 800341, 800783),
  "OAX" => Array(220000, -42000, 630000, 400000),
  "EAX" => Array(650000, 174000, 850000, 590000),
  "MPX" => Array(640178, 50000, 900341, 500783)
);

$projs = Array("DMX" => "proj=lcc,lat_1=42.0666,lat_2=43.2666,lat_0=41.5,lon_0=-93.5,x_0=1500000,y_0=1000000",
  "FSD" => "proj=lcc,lat_1=43.78,lat_2=45.21,lat_0=43,lon_0=-96,x_0=800000,y_0=100000",
  "ARX" => "proj=lcc,lat_1=43.78,lat_2=45.21,lat_0=43,lon_0=-92,x_0=800000,y_0=100000",
  "OAX" => "proj=lcc,lat_1=40.61,lat_2=41.78,lat_0=40,lon_0=-95.5,x_0=500000,y_0=0",
  "DVN" => "proj=tmerc,lat_0=36.666,lon_0=-90.16,k=0.9999,x_0=700000,y_0=0",
  "EAX" => "proj=tmerc,lat_0=36.166,lon_0=-94.5,k=0.9999,x_0=850000,y_0=0",
  "MPX" => "proj=lcc,lat_1=43.78,lat_2=45.21,lat_0=43,lon_0=-94,x_0=800000,y_0=100000"
);


if (strlen($img_x) > 0){
  include("queryl.php");
}

if (strlen($fips) == 0){
  $fips = '19169';
}

$wfos = Array("DMX" => "Des Moines",
 "DVN" => "Davenport",
 "ARX" => "LaCrosse",
 "MPX" => "Minneapolis",
 "FSD" => "Sioux Falls",
 "OAX" => "Omaha",
 "EAX" => "Pleasant Hill");

$connection = pg_connect("host=mesonet.agron.iastate.edu port=5432 dbname=postgis user=mesonet");

$query = "select name, cwa, extent(the_geom) from nws_counties 
   WHERE linkitem = '". $fips ."' GROUP by name, cwa";

$result = pg_exec($connection, $query);

pg_close($connection);

$row = @pg_fetch_array($result,0);

$box = substr($row["extent"], 6);
$site = $row["cwa"];
$cname = $row["name"];

echo "<font color=\"white\"><b>County:</b> ". $cname ."</font><br>\n";

//echo $row["extent"] ."<br>";

$tokens = split(",", $box);

$ll = split(" ", $tokens[0]);
$ur = split(" ", $tokens[1]);
$lon_ll = $ll[0];
$lat_ll = $ll[1];
$lon_ur = $ur[0];
$lat_ur = $ur[1];

//------------------------------------------------------------------

$projInObj = ms_newprojectionobj("proj=latlong");
$projOutObj = ms_newprojectionobj( $projs[$site] );

$ll_Point = ms_newpointobj();
$ll_Point->setXY($lon_ll, $lat_ll);         
$ll_Point = $ll_Point->project($projInObj, $projOutObj);
$ur_Point = ms_newpointobj();
$ur_Point->setXY($lon_ur, $lat_ur);         
$ur_Point = $ur_Point->project($projInObj, $projOutObj);

//echo $lon_ll ."<br>";
//echo $lat_ll ."<br>";
//echo $lon_ur ."<br>";
//echo $lat_ur ."<br>";

//echo "<hr>";

//echo $ll_Point->x - 100000 ."<br>";
//echo $ll_Point->y - 100000 ."<br>";
//echo $ur_Point->x + 100000 ."<br>";
//echo $ur_Point->y + 100000 ."<br>";

//echo "<hr>";

$radTimes = Array();
$fcontents = file('/mesonet/data/gis/'.$site.'.log');
while (list ($line_num, $line) = each ($fcontents)) {
  $radTimes[$line_num] = $line;
  $lastT = $line;
}

if (strlen($loop) > 0){

  $urls = Array();

  for ($i=0;$i<9;$i++){
   $imgi = 8 - $i;
   $radValid = $radTimes[$i];
   $radValid = substr($radValid, 0, -1);
   include("county2.php");
   $urls[$i] = $url;
  }

  include ("../iawarn/loop.php");
  array_reverse($urls);
  printHTML($urls, $radTimes);
} else {
  $radValid = $radTimes[8];
  $imgi = 0;
  include("county2.php");
  echo "<img src=\"". $url ."\">\n";
  echo "<font color=\"white\"><b>RADAR is valid at:</b> ". $lastT ."</font>";
  echo "<br><a href='county.php?fips=".$fips."&loop=yes'>Loop ME!!!</a>";
}
echo "</td><td>";

$imgi = 0;
$width = 200;
$height = 200;
include ("../iawarn/iawarn2.php");
echo "<font color=\"white\"><b>NEXRAD:</b> ". $wfos[$site] ."</font><br>\n";
echo "<form method=\"GET\" action=\"county.php\">\n";

echo "<input type=\"hidden\" value=\"".$fips."\" name=\"fips\">\n";
echo "<input type=\"hidden\" value=\"".$site."\" name=\"site\">\n";
echo "<input type=\"hidden\" value=\"".($Srect->minx)."\" name=\"lon_ll\">\n";
echo "<input type=\"hidden\" value=\"".($Srect->miny)."\" name=\"lat_ll\">\n";
echo "<input type=\"hidden\" value=\"".($Srect->maxx)."\" name=\"lon_ur\">\n";
echo "<input type=\"hidden\" value=\"".($Srect->maxy)."\" name=\"lat_ur\">\n";
echo "<input name=\"img\" type=\"image\" src=\"". $url ."\">\n";
?>
</form>

</td></tr></table>

<table>
<tr>
<td>
<b>Des Moines CWA</b><br>
 <br><a href="county.php?fips=19001">ADAIR</a>
 <br><a href="county.php?fips=19003">ADAMS</a>
 <br><a href="county.php?fips=19007">APPANOOSE</a>
 <br><a href="county.php?fips=19009">AUDUBON</a>
 <br><a href="county.php?fips=19013">BLACK HAWK</a>
 <br><a href="county.php?fips=19015">BOONE</a>
 <br><a href="county.php?fips=19017">BREMER</a>
 <br><a href="county.php?fips=19023">BUTLER</a>
 <br><a href="county.php?fips=19025">CALHOUN</a>
 <br><a href="county.php?fips=19027">CARROLL</a>
 <br><a href="county.php?fips=19029">CASS</a>
 <br><a href="county.php?fips=19033">CERRO GORDO</a>
 <br><a href="county.php?fips=19039">CLARKE</a>
 <br><a href="county.php?fips=19047">CRAWFORD</a>
 <br><a href="county.php?fips=19049">DALLAS</a>
 <br><a href="county.php?fips=19051">DAVIS</a>
 <br><a href="county.php?fips=19053">DECATUR</a>
 <br><a href="county.php?fips=19063">EMMET</a>
 <br><a href="county.php?fips=19069">FRANKLIN</a>
 <br><a href="county.php?fips=19073">GREENE</a>
 <br><a href="county.php?fips=19075">GRUNDY</a>
 <br><a href="county.php?fips=19077">GUTHRIE</a>
 <br><a href="county.php?fips=19079">HAMILTON</a>
 <br><a href="county.php?fips=19081">HANCOCK</a>
 <br><a href="county.php?fips=19083">HARDIN</a>
 <br><a href="county.php?fips=19091">HUMBOLDT</a>
 <br><a href="county.php?fips=19099">JASPER</a>
 <br><a href="county.php?fips=19109">KOSSUTH</a>
 <br><a href="county.php?fips=19117">LUCAS</a>
 <br><a href="county.php?fips=19121">MADISON</a>
 <br><a href="county.php?fips=19123">MAHASKA</a>
 <br><a href="county.php?fips=19125">MARION</a>
 <br><a href="county.php?fips=19127">MARSHALL</a>
 <br><a href="county.php?fips=19135">MONROE</a>
 <br><a href="county.php?fips=19147">PALO ALTO</a>
 <br><a href="county.php?fips=19151">POCAHONTAS</a>
 <br><a href="county.php?fips=19153">POLK</a>
 <br><a href="county.php?fips=19157">POWESHIEK</a>
 <br><a href="county.php?fips=19159">RINGGOLD</a>
 <br><a href="county.php?fips=19161">SAC</a>
 <br><a href="county.php?fips=19169">STORY</a>
 <br><a href="county.php?fips=19171">TAMA</a>
 <br><a href="county.php?fips=19173">TAYLOR</a>
 <br><a href="county.php?fips=19175">UNION</a>
 <br><a href="county.php?fips=19179">WAPELLO</a>
 <br><a href="county.php?fips=19181">WARREN</a>
 <br><a href="county.php?fips=19185">WAYNE</a>
 <br><a href="county.php?fips=19187">WEBSTER</a>
 <br><a href="county.php?fips=19189">WINNEBAGO</a>
 <br><a href="county.php?fips=19191">WINNESHIEK</a>
 <br><a href="county.php?fips=19195">WORTH</a>
 <br><a href="county.php?fips=19197">WRIGHT</a>
</td>
<td valign="top">
<b>Omaha CWA</b><br>
 <br><a href="county.php?fips=31003">ANTELOPE</a>
 <br><a href="county.php?fips=31011">BOONE</a>
 <br><a href="county.php?fips=31021">BURT</a>
 <br><a href="county.php?fips=31023">BUTLER</a>
 <br><a href="county.php?fips=31025">CASS</a>
 <br><a href="county.php?fips=31027">CEDAR</a>
 <br><a href="county.php?fips=31037">COLFAX</a>
 <br><a href="county.php?fips=31039">CUMING</a>
 <br><a href="county.php?fips=31053">DODGE</a>
 <br><a href="county.php?fips=31055">DOUGLAS</a>
 <br><a href="county.php?fips=19071">FREMONT</a>
 <br><a href="county.php?fips=31067">GAGE</a>
 <br><a href="county.php?fips=19085">HARRISON</a>
 <br><a href="county.php?fips=31095">JEFFERSON</a>
 <br><a href="county.php?fips=31097">JOHNSON</a>
 <br><a href="county.php?fips=31107">KNOX</a>
 <br><a href="county.php?fips=31109">LANCASTER</a>
 <br><a href="county.php?fips=31119">MADISON</a>
 <br><a href="county.php?fips=19129">MILLS</a>
 <br><a href="county.php?fips=19133">MONONA</a>
 <br><a href="county.php?fips=19137">MONTGOMERY</a>
 <br><a href="county.php?fips=31127">NEMAHA</a>
 <br><a href="county.php?fips=31131">OTOE</a>
 <br><a href="county.php?fips=19145">PAGE</a>
 <br><a href="county.php?fips=31133">PAWNEE</a>
 <br><a href="county.php?fips=31139">PIERCE</a>
 <br><a href="county.php?fips=31141">PLATTE</a>
 <br><a href="county.php?fips=19155">POTTAWATTAMIE</a>
 <br><a href="county.php?fips=31147">RICHARDSON</a>
 <br><a href="county.php?fips=31151">SALINE</a>
 <br><a href="county.php?fips=31153">SARPY</a>
 <br><a href="county.php?fips=31155">SAUNDERS</a>
 <br><a href="county.php?fips=31159">SEWARD</a>
 <br><a href="county.php?fips=19165">SHELBY</a>
 <br><a href="county.php?fips=31167">STANTON</a>
 <br><a href="county.php?fips=31173">THURSTON</a>
 <br><a href="county.php?fips=31177">WASHINGTON</a>
 <br><a href="county.php?fips=31179">WAYNE</a>
</td>
<td valign="top">
<b>Sioux Falls CWA</b><br>
 <br><a href="county.php?fips=46003">AURORA</a>
 <br><a href="county.php?fips=46005">BEADLE</a>
 <br><a href="county.php?fips=46009">BON HOMME</a>
 <br><a href="county.php?fips=46011">BROOKINGS</a>
 <br><a href="county.php?fips=46015">BRULE</a>
 <br><a href="county.php?fips=19021">BUENA VISTA</a>
 <br><a href="county.php?fips=46023">CHARLES MIX</a>
 <br><a href="county.php?fips=19035">CHEROKEE</a>
 <br><a href="county.php?fips=46025">CLARK</a>
 <br><a href="county.php?fips=19041">CLAY</a>
 <br><a href="county.php?fips=46027">CLAY</a>
 <br><a href="county.php?fips=46029">CODINGTON</a>
 <br><a href="county.php?fips=27033">COTTONWOOD</a>
 <br><a href="county.php?fips=31043">DAKOTA</a>
 <br><a href="county.php?fips=46035">DAVISON</a>
 <br><a href="county.php?fips=46039">DEUEL</a>
 <br><a href="county.php?fips=19059">DICKINSON</a>
 <br><a href="county.php?fips=31051">DIXON</a>
 <br><a href="county.php?fips=46043">DOUGLAS</a>
 <br><a href="county.php?fips=46053">GREGORY</a>
 <br><a href="county.php?fips=46057">HAMLIN</a>
 <br><a href="county.php?fips=46061">HANSON</a>
 <br><a href="county.php?fips=46067">HUTCHINSON</a>
 <br><a href="county.php?fips=19093">IDA</a>
 <br><a href="county.php?fips=27063">JACKSON</a>
 <br><a href="county.php?fips=46073">JERAULD</a>
 <br><a href="county.php?fips=46077">KINGSBURY</a>
 <br><a href="county.php?fips=46079">LAKE</a>
 <br><a href="county.php?fips=46083">LINCOLN</a>
 <br><a href="county.php?fips=27083">LYON</a>
 <br><a href="county.php?fips=19119">LYON</a>
 <br><a href="county.php?fips=46087">MCCOOK</a>
 <br><a href="county.php?fips=46097">MINER</a>
 <br><a href="county.php?fips=46099">MINNEHAHA</a>
 <br><a href="county.php?fips=46101">MOODY</a>
 <br><a href="county.php?fips=27101">MURRAY</a>
 <br><a href="county.php?fips=27105">NOBLES</a>
 <br><a href="county.php?fips=19141">O'BRIEN</a>
 <br><a href="county.php?fips=19143">OSCEOLA</a>
 <br><a href="county.php?fips=27117">PIPESTONE</a>
 <br><a href="county.php?fips=19149">PLYMOUTH</a>
 <br><a href="county.php?fips=27133">ROCK</a>
 <br><a href="county.php?fips=46111">SANBORN</a>
 <br><a href="county.php?fips=19167">SIOUX</a>
 <br><a href="county.php?fips=46125">TURNER</a>
 <br><a href="county.php?fips=46127">UNION</a>
 <br><a href="county.php?fips=19193">WOODBURY</a>
 <br><a href="county.php?fips=46135">YANKTON</a>
</td>
<td valign="top">
<b>LaCrosse CWA</b><br>
 <br><a href="county.php?fips=55001">ADAMS</a>
 <br><a href="county.php?fips=19005">ALLAMAKEE</a>
 <br><a href="county.php?fips=55011">BUFFALO</a>
 <br><a href="county.php?fips=19037">CHICKASAW</a>
 <br><a href="county.php?fips=55019">CLARK</a>
 <br><a href="county.php?fips=19043">CLAYTON</a>
 <br><a href="county.php?fips=27039">DODGE</a>
 <br><a href="county.php?fips=19065">FAYETTE</a>
 <br><a href="county.php?fips=27045">FILLMORE</a>
 <br><a href="county.php?fips=19067">FLOYD</a>
 <br><a href="county.php?fips=27055">HOUSTON</a>
 <br><a href="county.php?fips=19089">HOWARD</a>
 <br><a href="county.php?fips=55053">JACKSON</a>
 <br><a href="county.php?fips=55057">JUNEAU</a>
 <br><a href="county.php?fips=55063">LA CROSSE</a>
 <br><a href="county.php?fips=19131">MITCHELL</a>
 <br><a href="county.php?fips=55081">MONROE</a>
 <br><a href="county.php?fips=27099">MOWER</a>
 <br><a href="county.php?fips=27109">OLMSTED</a>
 <br><a href="county.php?fips=55103">RICHLAND</a>
 <br><a href="county.php?fips=55119">TAYLOR</a>
 <br><a href="county.php?fips=55121">TREMPEALEAU</a>
 <br><a href="county.php?fips=55123">VERNON</a>
 <br><a href="county.php?fips=27157">WABASHA</a>
 <br><a href="county.php?fips=27169">WINONA</a>
</td>
<td valign="top">
<b>Davenport CWA</b><br>
<br><a href="county.php?fips=19011">BENTON</a>
 <br><a href="county.php?fips=19019">BUCHANAN</a>
 <br><a href="county.php?fips=17011">BUREAU</a>
 <br><a href="county.php?fips=17015">CARROLL</a>
 <br><a href="county.php?fips=19031">CEDAR</a>
 <br><a href="county.php?fips=19045">CLINTON</a>
 <br><a href="county.php?fips=19055">DELAWARE</a>
 <br><a href="county.php?fips=19057">DES MOINES</a>
 <br><a href="county.php?fips=19061">DUBUQUE</a>
 <br><a href="county.php?fips=55043">GRANT</a>
 <br><a href="county.php?fips=17067">HANCOCK</a>
 <br><a href="county.php?fips=17071">HENDERSON</a>
 <br><a href="county.php?fips=17073">HENRY</a>
 <br><a href="county.php?fips=19087">HENRY</a>
 <br><a href="county.php?fips=19095">IOWA</a>
 <br><a href="county.php?fips=19097">JACKSON</a>
 <br><a href="county.php?fips=19101">JEFFERSON</a>
 <br><a href="county.php?fips=17085">JO DAVIESS</a>
 <br><a href="county.php?fips=19103">JOHNSON</a>
 <br><a href="county.php?fips=19105">JONES</a>
 <br><a href="county.php?fips=19107">KEOKUK</a>
 <br><a href="county.php?fips=19111">LEE</a>
 <br><a href="county.php?fips=19113">LINN</a>
 <br><a href="county.php?fips=19115">LOUISA</a>
 <br><a href="county.php?fips=17109">MCDONOUGH</a>
 <br><a href="county.php?fips=17131">MERCER</a>
 <br><a href="county.php?fips=19139">MUSCATINE</a>
 <br><a href="county.php?fips=17155">PUTNAM</a>
 <br><a href="county.php?fips=17161">ROCK ISLAND</a>
 <br><a href="county.php?fips=19163">SCOTT</a>
 <br><a href="county.php?fips=17177">STEPHENSON</a>
 <br><a href="county.php?fips=19177">VAN BUREN</a>
 <br><a href="county.php?fips=17187">WARREN</a>
 <br><a href="county.php?fips=19183">WASHINGTON</a>
 <br><a href="county.php?fips=17195">WHITESIDE</a>
</td>
</tr>
</table>


