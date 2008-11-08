<?php
/* Create a table of soil temperature probabilities based on obs? */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$THISPAGE="networks-agclimate";
include("$rootpath/include/header.php");
include("$rootpath/include/imagemaps.php");

$station = isset($_GET["station"]) ? $_GET['station']: "A130209";
$tstr = isset($_GET["tstr"]) ? $_GET['tstr']: "50,45,40,35,32,28,23";

$conn = iemdb("isuag");
$rs = pg_prepare($conn, "spring", "SELECT extract(year from valid) as yr,
      max(extract(doy from valid)) as v from daily WHERE station = $1 and c30 < $2 and 
      extract(month from valid) < 7 and c30_f != 'e' GROUP by yr");
$rs = pg_prepare($conn, "fall", "SELECT extract(year from valid) as yr,
      min(extract(doy from valid)) as v from daily WHERE station = $1 and c30 < $2 and
      extract(month from valid) > 6 and c30_f != 'e' GROUP by yr");

$thresholds = explode(",",$tstr);
$tblrows = Array();

$row1 = "<tr><th>Date:</th>";
while (list($k,$thres) = each($thresholds))
{
  $row1 .= "<th>$thres</th>";
  $rs = pg_execute($conn, "spring", Array($station,$thres));
  $cnts = Array();
  $yrs = pg_num_rows($rs);
  for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
  {
    @$cnts[ $row["v"] ] += 1;
  }
  $probs = Array();
  $running = $yrs;
  for ($i=0;$i<182;$i++) {
    if (array_key_exists($i,$cnts)){ $running -= $cnts[$i]; }
    $probs[$i] = $running;
  }
  /* Day Sampler */
  for ($i=0;$i<182;$i=$i+5) {
    $ts = mktime(0,0,0,1,1,2000) + ($i * 86400);
    @$tblrows[$i] .= sprintf("<td>%.0f</td>", $probs[$i]/$yrs*100);
  }
}
$spring = "<table>$row1</tr>";
/* Print webpage */
for ($i=0;$i<182;$i=$i+5) {
  $ts = mktime(0,0,0,1,1,2000) + ($i * 86400);
  $spring .= sprintf("<tr><th>%s</th>%s</tr>", date("M d", $ts), $tblrows[$i]);
}
$spring .= "</table>";

/* ________________________FALL ______________ */
$tblrows = Array();
reset($thresholds);
while (list($k,$thres) = each($thresholds))
{
  $rs = pg_execute($conn, "fall", Array($station,$thres));
  $cnts = Array();
  $yrs = pg_num_rows($rs);
  for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
  {
    @$cnts[ $row["v"] ] += 1;
  }
  $probs = Array();
  $running = 0;
  for ($i=182;$i<366;$i++) {
    if (array_key_exists($i,$cnts)){ $running += $cnts[$i]; }
    $probs[$i] = $running;
  }
  /* Day Sampler */
  for ($i=182;$i<366;$i=$i+5) {
    $ts = mktime(0,0,0,1,1,2000) + ($i * 86400);
    @$tblrows[$i] .= sprintf("<td>%.0f</td>", $probs[$i]/$yrs*100);
  }
}
$fall = "<table>$row1</tr>";
/* Print webpage */
for ($i=182;$i<366;$i=$i+5) {
  $ts = mktime(0,0,0,1,1,2000) + ($i * 86400);
  $fall .= sprintf("<tr><th>%s</th>%s</tr>", date("M d", $ts), $tblrows[$i]);
}
$fall .= "</table>";
?>

<h3>4 inch soil temperature probabilities</h3>

<p>This application computes soil temperature exceedance based on the
observation record of a ISU Ag Climate site.  The average daily 4 inch
soil temperature is used in this calculation.
<ul>
 <li>Spring: The values represent the percentage of years that a temperature
below the given threshold was observed <strong>after</strong> a given date.</li>
 <li>Fall: The values represent the percentage of years that a temperature
below the given threshold was observed <strong>before</strong> a given date.</li>
</ul>



<form method="GET">
<p><b>Select Station:</b><?php echo isuagSelect($station); ?>
<p><b>Thresholds:</b><input type="text" value="<?php echo $tstr; ?>" name="tstr"> <i>Comma Seperated</i>
<br />
<input type="submit" value="Request">
</form>

<table cellpadding="5" cellspacing="0" border="1">
<tr>
<td valign="top">
 <h3>Spring Probabilities<br />January 1rst to given date</h3>
 <?php echo $spring; ?>
</td>
<td valign="top">
 <h3>Fall Probabilities<br />July 1rst to given date</h3>
 <?php echo $fall; ?>
</td>
</table>

<?php include("$rootpath/include/footer.php"); ?>
