<?php 
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/feature.php");
$day = isset($_GET["day"]) ? substr($_GET["day"],0,10) : die("No date specified");
$offset = isset($_GET["offset"]) ? $_GET["offset"] : 0;

$dbconn = iemdb("mesosite");
$rs = pg_prepare($dbconn, "yesterday", "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE valid < $1 ORDER by valid DESC limit 1");
$rs = pg_prepare($dbconn, "today", "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE date(valid) = $1");
$rs = pg_prepare($dbconn, "tomorrow", "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE valid > ($1::date + '1 day'::interval) 
              ORDER by valid ASC limit 1");

$q = "today";
if ($offset == "-1"){ $q = "yesterday"; }
else if ($offset == "+1") {$q = "tomorrow";}
$result = pg_execute($dbconn, $q, Array($day));

if (pg_num_rows($result) == 0){ die("Feature Not Found"); }

$TITLE = "IEM | Past Feature"; 
$THISPAGE = "iem-feature";
include("$rootpath/include/header.php"); 

$row = pg_fetch_array($result,0);
$day = $row["d"];
$thumb = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s_s.gif", $row["imageref"]);
$big = sprintf("http://mesonet.agron.iastate.edu/onsite/features/%s.gif", $row["imageref"]);

?>
<a href="cat.php?day=<?php echo $day; ?>&offset=-1">Previous Feature</a> &nbsp; &nbsp; <a href="cat.php?day=<?php echo $day; ?>&offset=+1">Next Feature</a>
<hr />
<div style="width: 640px;">
<div style="float: left; padding: 5px; ">
<img src="<?php echo $thumb; ?>" style="margin: 5px;">
<br /><a href="<?php echo $big; ?>">View larger image</a>
<br /><?php echo $row["caption"]; ?>
</div>
<?php
  echo "<h3>". $row["title"] ."</h3>\n";
  echo "<font size='-1' style='color:black'>". $row["webdate"] ."</font>\n";
  echo "<br><div class='story'>". $row["story"] ;
  if ($row["voting"] == 't' && (intval($row["good"]) > 0 || intval($row["bad"]) > 0))
  {
    echo "<br /><br /><b>Voting:</b><br />Good = ". $row["good"] ." <br />Bad = ". $row["bad"] ;
  }
  echo "<br />". printTags(explode(",", $row["tags"]));
?>
</div>


<?php include("$rootpath/include/footer.php"); ?>

