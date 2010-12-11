<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$THISPAGE = "severe-river";
include("$rootpath/include/header.php");
include("$rootpath/include/wfoLocs.php");
include("$rootpath/include/forms.php");
$wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3): "DMX";
$state = isset($_GET["state"]) ? substr($_GET["state"],0,3): "IA";

$postgis = iemdb("postgis");
$sevcol = Array(
 "N" =>"#0f0",
 "0" =>"#ff0",
 "1" =>"#ff9900",
 "2" =>"#f00",
 "3" =>"#f0f",
 "U" =>"#fff");

$nwsli_limiter = "";
if (isset($_GET["dvn"])){
 $nwsli_limiter = "and r.nwsli IN ('FLTI2', 'CMMI4', 'LECI4', 'RCKI2', 'ILNI2', 'MUSI4', 'NBOI2', 'KHBI2', 'DEWI4', 'CNEI4', 'CJTI4', 'WAPI4','LNTI4', 'CMOI2', 'JOSI2', 'MLII2','GENI2')";
 echo "<style>
#iem-header {
  display: none;
  visibility: hidden;
}
#iem-footer {
  display: none;
  visibility: hidden;
}
body {
  background: #fff;
  font-size: smaller;
}
</style>";
}

if (isset($_GET["state"])){
 $rs = pg_prepare($postgis, "SELECT", "select h.name, h.river_name, h.nwsli, foo.wfo, foo.eventid, foo.phenomena, r.severity, r.stage_text, r.flood_text, r.forecast_text, 
   sumtxt(c.name || ', ') as counties from hvtec_nwsli h, 
   riverpro r, nws_ugc c, 
  (select distinct hvtec_nwsli, ugc, eventid, phenomena, wfo from warnings_". date("Y") ." WHERE 
   status NOT IN ('EXP','CAN') and phenomena = 'FL' and 
   significance = 'W' and hvtec_nwsli IN (select nwsli from hvtec_nwsli WHERE state = $1 and" .
   		"expire > now())" .
   		" and expire > now()) as foo
   WHERE foo.hvtec_nwsli = r.nwsli and r.nwsli = h.nwsli $nwsli_limiter
   and c.ugc = foo.ugc GROUP by h.river_name, h.name, h.nwsli, foo.wfo, foo.eventid, foo.phenomena, r.severity,
   r.stage_text, r.flood_text, r.forecast_text");
 $rs = pg_execute($postgis, "SELECT", Array($state));
 $ptitle = "<h3>River Forecast Point Monitor by State</h3>";
} else {
 $rs = pg_prepare($postgis, "SELECT", "select h.name, h.river_name, h.nwsli, foo.wfo, foo.eventid, foo.phenomena, r.severity, r.stage_text, r.flood_text, r.forecast_text, 
   sumtxt(c.name || ', ') as counties
   from hvtec_nwsli h, riverpro r, nws_ugc c,
  (select distinct hvtec_nwsli, ugc, eventid, phenomena, wfo from warnings_". date("Y") ." WHERE 
   status NOT IN ('EXP','CAN') and phenomena = 'FL' and 
   significance = 'W' and wfo = $1 and expire > now()) as foo
   WHERE foo.hvtec_nwsli = r.nwsli and r.nwsli = h.nwsli $nwsli_limiter
   and c.ugc = foo.ugc GROUP by h.river_name, h.name, h.nwsli, foo.wfo, foo.eventid, foo.phenomena, r.severity,
   r.stage_text, r.flood_text, r.forecast_text");
 $rs = pg_execute($postgis, "SELECT", Array($wfo));
 $ptitle = "<h3>River Forecast Point Monitor by NWS WFO</h3>";
}


$rivers = Array();
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $river = $row["river_name"];
  $uri = sprintf("%s/vtec/#%s-O-%s-K%s-%s-%s-%04d", $rooturl, date("Y"),
        "NEW", $row["wfo"], $row["phenomena"],
        "W", $row["eventid"]);


  @$rivers[$river] .= sprintf("<tr><th style='background: %s;'>%s<br />%s</th><td><a href='%s'>%s</a></td></th><td>%s</td><td>%s</td><td>%s</td></tr>",$sevcol[$row["severity"]], $row["name"], 
   $row["nwsli"], $uri, $row["counties"], $row["stage_text"], $row["flood_text"], 
   $row["forecast_text"]);
}
echo $ptitle;
echo "<p><form method='GET' name='wfo'>";
echo 'Select by NWS Forecast Office:'. wfoSelect($wfo);
echo "<input type='submit' value='Select by WFO'>";
echo "</form>";
?>
<p><form method='GET' name='state'>
Select by State: 
<select name="state">
 <option value="AL" <?php if ($state == "AL") echo "SELECTED"; ?>>Alabama
 <option value="AK" <?php if ($state == "AK") echo "SELECTED"; ?>>Alaska
 <option value="AR" <?php if ($state == "AR") echo "SELECTED"; ?>>Arkansas
 <option value="AZ" <?php if ($state == "AZ") echo "SELECTED"; ?>>Arizona
 <option value="CA" <?php if ($state == "CA") echo "SELECTED"; ?>>California
 <option value="CO" <?php if ($state == "CO") echo "SELECTED"; ?>>Colorado
 <option value="CT" <?php if ($state == "CT") echo "SELECTED"; ?>>Connecticut
 <option value="DE" <?php if ($state == "DE") echo "SELECTED"; ?>>Delaware
 <option value="FL" <?php if ($state == "FL") echo "SELECTED"; ?>>Florida
 <option value="GA" <?php if ($state == "GA") echo "SELECTED"; ?>>Georgia
 <option value="HI" <?php if ($state == "HI") echo "SELECTED"; ?>>Hawaii
 <option value="ID" <?php if ($state == "ID") echo "SELECTED"; ?>>Idaho
 <option value="IL" <?php if ($state == "IL") echo "SELECTED"; ?>>Illinois
 <option value="IN" <?php if ($state == "IN") echo "SELECTED"; ?>>Indiana
 <option value="IA" <?php if ($state == "IA") echo "SELECTED"; ?>>Iowa
 <option value="KS" <?php if ($state == "KS") echo "SELECTED"; ?>>Kansas
 <option value="KY" <?php if ($state == "KY") echo "SELECTED"; ?>>Kentucky
 <option value="LA" <?php if ($state == "LA") echo "SELECTED"; ?>>Louisana
 <option value="MN" <?php if ($state == "MN") echo "SELECTED"; ?>>Maine
 <option value="MD" <?php if ($state == "MD") echo "SELECTED"; ?>>Maryland
 <option value="MA" <?php if ($state == "MA") echo "SELECTED"; ?>>Massachusetts
 <option value="MI" <?php if ($state == "MI") echo "SELECTED"; ?>>Michigan
 <option value="MN" <?php if ($state == "MN") echo "SELECTED"; ?>>Minnesota
 <option value="MS" <?php if ($state == "MS") echo "SELECTED"; ?>>Mississippi
 <option value="MO" <?php if ($state == "MO") echo "SELECTED"; ?>>Missouri
 <option value="MT" <?php if ($state == "MT") echo "SELECTED"; ?>>Montana
 <option value="NE" <?php if ($state == "NE") echo "SELECTED"; ?>>Nebraska
 <option value="NH" <?php if ($state == "NH") echo "SELECTED"; ?>>New Hampshire
 <option value="NC" <?php if ($state == "NC") echo "SELECTED"; ?>>North Carolina
 <option value="ND" <?php if ($state == "ND") echo "SELECTED"; ?>>North Dakota
 <option value="NV" <?php if ($state == "NV") echo "SELECTED"; ?>>Nevada
 <option value="NH" <?php if ($state == "NH") echo "SELECTED"; ?>>New Hampshire
 <option value="NJ" <?php if ($state == "NJ") echo "SELECTED"; ?>>New Jersey
 <option value="NM" <?php if ($state == "NM") echo "SELECTED"; ?>>New Mexico
 <option value="NY" <?php if ($state == "NY") echo "SELECTED"; ?>>New York
 <option value="OH" <?php if ($state == "OH") echo "SELECTED"; ?>>Ohio
 <option value="OK" <?php if ($state == "OK") echo "SELECTED"; ?>>Oklahoma
 <option value="OR" <?php if ($state == "OR") echo "SELECTED"; ?>>Oregon
 <option value="PA" <?php if ($state == "PA") echo "SELECTED"; ?>>Pennsylvania
 <option value="RI" <?php if ($state == "RI") echo "SELECTED"; ?>>Rhode Island
 <option value="SC" <?php if ($state == "SC") echo "SELECTED"; ?>>South Carolina
 <option value="SD" <?php if ($state == "SD") echo "SELECTED"; ?>>South Dakota
 <option value="TN" <?php if ($state == "TN") echo "SELECTED"; ?>>Tennessee
 <option value="TX" <?php if ($state == "TX") echo "SELECTED"; ?>>Texas
 <option value="UT" <?php if ($state == "UT") echo "SELECTED"; ?>>Utah
 <option value="VT" <?php if ($state == "VT") echo "SELECTED"; ?>>Vermont
 <option value="VA" <?php if ($state == "VA") echo "SELECTED"; ?>>Virginia
 <option value="WA" <?php if ($state == "WA") echo "SELECTED"; ?>>Washington
 <option value="WV" <?php if ($state == "WV") echo "SELECTED"; ?>>West Virginia
 <option value="WI" <?php if ($state == "WI") echo "SELECTED"; ?>>Wisconsin
 <option value="WY" <?php if ($state == "WY") echo "SELECTED"; ?>>Wyoming
</select>
<input type='submit' value="Select by State">
</form>

<table border='1' cellpadding='2' cellspacing='0' style="margin: 5px;">
<tr>
 <th>Key:</th>
 <td style="background: #ff0;">Near Flood Stage</td>
 <td style="background: #ff9900;">Minor Flooding</td>
 <td style="background: #f00;">Moderate Flooding</td>
 <td style="background: #f0f;">Major Flooding</td>
</tr></table>

<?php
echo "<p><table border='1' cellpadding='2' cellspacing='0'>";
$rvs = array_keys($rivers);
asort($rvs);

while (list($idx, $key) = each($rvs))
{
  echo "<tr><th colspan='5' style='background: #eee; text-align: left;'>$key</th></tr>";
  echo $rivers[$key];

}

echo "</table>";

include("$rootpath/include/footer.php");
?>
