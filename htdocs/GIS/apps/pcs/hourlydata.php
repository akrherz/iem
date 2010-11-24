<?php
 // -----------------------------------------------------------------
 // request.php
 //   Give the user the climate data in the format they want...
 // -----------------------------------------------------------------

// Load MapScript


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
   $row["p01i"]
));
} // End addPoint 

if (strlen($year) == 0){
  $year = date('Y');
} if (strlen($month) == 0){
  $month = date('m');
} if (strlen($day) == 0){
  $day = date('d');
} if (strlen($hour) == 0){
  $hour = date('H');
}
$ts = mktime($hour,0,0, $month, $day, $year);
$sqlDate = strftime('%Y-%m-%d %H:00', $ts);
$filePre = strftime('%m%d', $ts) ."_coop";
$cgi = strftime('year=%Y&month=%m&day=%d&hour=%H', $ts);


$pgcon = pg_connect("iemdb", 5432, "postgis");
pg_exec($pgcon, "SET TIME ZONE 'GMT'");
$rs = pg_exec($pgcon, "select s.*, c.*, 
   to_char(c.valid, 'YYYYMMDD') as cvalid from 
   stations s, hp_2002 c WHERE c.station = s.id
   and c.valid = '". $sqlDate ."' ");

pg_close($pgcon);


$shpFname = "/home/httpd/html/tmp/". $filePre;
$shpFile = ms_newShapeFileObj($shpFname, MS_SHP_POINT);
$dbfFile = dbase_create( $shpFname.".dbf", array(
   array("SITE", "C", 6),
   array("NAME", "C", 50),
   array("PREC", "N", 8, 2)
));


for( $i=0; $row = @pg_fetch_array($rs,$i); $i++){
  addPoint($row);
} // End of for

$shpFile->free();
dbase_close($dbfFile);

// Generate zip file
chdir("/home/httpd/html/tmp/");
popen("zip ".$filePre.".zip ".$filePre.".shp ".$filePre.".shx ".$filePre.".dbf", 'r');  

echo "Shapefile Generation Complete.<br>";
echo "Please download this <a href=\"/tmp/".$filePre.".zip\">zipfile</a>.";

?>

<p><a href="index.php?<?php echo $cgi; ?>">Here</a> is a link back to where you came from.
