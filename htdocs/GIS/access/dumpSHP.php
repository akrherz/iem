<?php
 // -----------------------------------------------------------------
 // dumpSHP.php
 //   Give the user the climate data in the format they want...
 // -----------------------------------------------------------------



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
   $row["sname"], 
   $row["cvalid"],
   $row["ctime"],
   $row["tmpf"],
   $row["dwpf"]
));
} // End addPoint 

$filePre = time() ."_iema";

include('../../include/iemaccess.php');

$iem = new IEMAccess();

$rs = pg_exec($iem->dbconn, "SELECT x(geom) as longitude, y(geom) as latitude, 
  to_char(valid, 'YYYYMMDD') as cvalid, to_char(valid, 'HH24MI') as ctime, 
  * from current WHERE 
    tmpf > -90 and dwpf > -90  and valid > (CURRENT_TIMESTAMP - '4 hours'::interval)::timestamp");

pg_close($iem->dbconn);

mkdir("/home/httpd/html/tmp/". $filePre);
$shpFname = "/home/httpd/html/tmp/". $filePre ."/iemaccess";
$shpFile = ms_newShapeFileObj($shpFname, MS_SHP_POINT);
$dbfFile = dbase_create( $shpFname.".dbf", array(
   array("SITE", "C", 10),
   array("NAME", "C", 50),
   array("OB_DATE", "D"),
   array("OB_TIME", "C", 4),
   array("AIR_TMP_F", "N", 3, 0),
   array("AIR_DEW_F", "N", 3, 0)
));


for( $i=0; $row = @pg_fetch_array($rs,$i); $i++){
  addPoint($row);
} // End of for

$shpFile->free();
dbase_close($dbfFile);

// Generate zip file
chdir("/home/httpd/html/tmp/". $filePre);
popen("zip iemaccess.zip iemaccess.shp iemaccess.shx iemaccess.dbf", 'r');  

header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=iemaccess.zip");

if ($file = fopen($shpFname .".zip", 'rb')) {
  while(!feof($file) and (connection_status()==0)) {
   print(fread($file, 1024*8));
    flush();
  }
 $status = (connection_status()==0);
  fclose($file);
}
?>
