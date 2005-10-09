<?php
include("../../../../config/settings.inc.php");
 // -----------------------------------------------------------------
 // request.php
 //   Give the user the climate data in the format they want...
 // -----------------------------------------------------------------

// Load MapScript
dl($mapscript);
include("$rootpath/include/database.inc.php");
$month = isset($_GET["month"]) ? $_GET["month"] : die();
$day = isset($_GET["day"]) ? $_GET["day"] : die();

function addPoint( $row ){
  GLOBAL $shpFile, $dbfFile;

  // Create the shape
  $shp = ms_newShapeObj(MS_SHAPE_POINT);
  $pt = ms_newPointobj();
  $pt->setXY( $row["longitude"], $row["latitude"], 0);
  $line = ms_newLineObj();
  $line->add( $pt );
  $shp->add($line);
  $shpFile->addShape($shp);

  dbase_add_record($dbfFile, array(
   $row["station"], 
   $row["name"],
   $row["years"],
   $row["cvalid"],
   $row["high"],
   $row["low"],
   $row["precip"],
   $row["max_precip"],
   $row["max_precip_yr"],
   $row["max_high"],
   $row["max_low"],
   $row["min_high"],
   $row["min_low"],
   $row["max_high_yr"],
   $row["max_low_yr"],
   $row["min_high_yr"],
   $row["min_low_yr"]
));
} // End addPoint 

if (strlen($month) == 0){
  $month = date('m');
} if (strlen($day) == 0){
  $day = date('d');
}
$ts = mktime(0,0,0, $month, $day, 2000);
$sqlDate = strftime('%Y-%m-%d', $ts);
$filePre = strftime('%m%d', $ts) ."_coop";


$pgcon = iemdb("coop");
$rs = pg_exec($pgcon, "select s.*, c.*, 
   to_char(c.valid, 'YYYYMMDD') as cvalid from 
   stations s, climate c WHERE c.station = lower(s.id) 
   and c.valid = '". $sqlDate ."' ");

pg_close($pgcon);


$shpFname = "/var/www/htdocs/tmp/". $filePre;
$shpFile = ms_newShapeFileObj($shpFname, MS_SHP_POINT);
$dbfFile = dbase_create( $shpFname.".dbf", array(
   array("SITE", "C", 6),
   array("NAME", "C", 50),
   array("CRECORD", "N", 5, 0),
   array("DATE", "D"),
   array("AVG_HIGH", "N", 3, 0),
   array("AVG_LOW", "N", 3, 0), 
   array("AVG_PREC", "N", 8, 2), 
   array("MAX_PREC", "N", 8, 2), 
   array("MAX_PR_YR", "N", 4, 0), 
   array("MAX_HIGH", "N", 3, 0), 
   array("MAX_LOW", "N", 3, 0), 
   array("MIN_HIGH", "N", 3, 0), 
   array("MIN_LOW", "N", 3, 0), 
   array("MAX_HI_YR", "N", 4, 0), 
   array("MAX_LO_YR", "N", 4, 0), 
   array("MIN_HI_YR", "N", 4, 0), 
   array("MIN_LO_YR", "N", 4, 0) 
));


for( $i=0; $row = @pg_fetch_array($rs,$i); $i++){
  addPoint($row);
} // End of for

$shpFile->free();
dbase_close($dbfFile);

// Generate zip file
chdir("/var/www/htdocs/tmp/");
popen("zip ".$filePre.".zip ".$filePre.".shp ".$filePre.".shx ".$filePre.".dbf", 'r');  

echo "Shapefile Generation Complete.<br>";
echo "Please download this <a href=\"/tmp/".$filePre.".zip\">zipfile</a>.";

?>

<p><a href="index.php?month=<?php echo $month; ?>&day=<?php echo $day; ?>">Here</a> is a link back to where you came from.
