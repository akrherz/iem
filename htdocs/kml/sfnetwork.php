<?php
/* Sucks to render a KML */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connect = iemdb("access");
$year = date("Y");
/* Now we fetch warning and perhaps polygon */
$query2 = "SELECT *, askml(t.geom) as kml, t.name as sname
           from current c, summary_${year} s, stations t
           WHERE c.iemid = s.iemid and c.iemid = t.iemid and 
           s.day = 'TODAY' and 
           t.network = 'KCCI' and valid > (now() - '30 minutes'::interval)";

$result = pg_exec($connect, $query2);

header("Content-Type: application/vnd.google-earth.kml+xml");
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
   <Style id=\"iemstyle\">
     <IconStyle>
      <scale>0.8</scale>
      <Icon>
        <href>http://www.schoolnet8.com/favicon.ico</href>
      </Icon>
     </IconStyle>
     <BalloonStyle>
      <bgColor>ffffffff</bgColor>
    </BalloonStyle>
  </Style>";
for ($i=0;$row=@pg_fetch_array($result,$i);$i++)
{
  echo "<Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Site Name:</i></font> ". $row["sname"] ."
   <br /><font color=\"red\"><i>Temperature:</i></font> ". $row["tmpf"] ."
   <br /><font color=\"red\"><i>Dew Point:</i></font> ". $row["dwpf"] ." 
   <br /><font color=\"red\"><i>Today Rainfall:</i></font> ". $row["pday"] ." 
   </p>
        ]]>
    </description>
    <styleUrl>#iemstyle</styleUrl>
    <name>". $row["tmpf"] ."</name>\n";
echo $row["kml"];
echo "</Placemark>";
}
echo "
 </Document>
</kml>";

?>
