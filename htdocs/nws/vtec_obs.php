<?php
 include("../../config/settings.inc.php");
 define("IEM_APPID", 108);
 $wfo = isset($_REQUEST["wfo"]) ? $_REQUEST["wfo"] : 'DMX';
$year = isset($_REQUEST["year"]) ? intval($_REQUEST["year"]): 2012;
$sid = isset($_REQUEST["sid"]) ? intval($_REQUEST["sid"]): 1;
$eid = isset($_REQUEST["eid"]) ? intval($_REQUEST["eid"]): 999;
$rhthres = isset($_REQUEST["relh"]) ? floatval($_REQUEST["relh"]): 25;
$skntthres = isset($_REQUEST["sknt"]) ? floatval($_REQUEST["sknt"]): 25;
$vsbythres = isset($_REQUEST["vsby"]) ? floatval($_REQUEST["vsby"]): 0.25;
$mode = isset($_REQUEST["mode"])? substr($_REQUEST["mode"],0,4): 'FW.W';
$ar = explode(".", $mode);
$phenomena = $ar[0];
$significance = $ar[1];

 $TITLE = "IEM | NWS Watch/Warning/Advisory + ASOS Observations";

  include("$rootpath/include/header.php"); 
  include("$rootpath/include/wfoLocs.php");
  include("$rootpath/include/forms.php");
  include("$rootpath/include/mlib.php");
  ?>

  <h2>NWS Watch/Warning/Advisory + ASOS Observations</h2>
  
  <p>This app allows you to view an office's warnings for a year and
  then looks for ASOS/AWOS observations valid for the warning period. The observations
  presented are coded like:
  <br />ID DDHHMI TMPF/DWPF RELH VSBY SKNT/GUST
  <br />Where ID is the station identifier, DDHHMI is the day-hour-minute of the
  observation in UTC, TMPF is the air temperature in Fahrenheit, DWPF is the
  dew point temperature in Fahrenheit, RELH is the relative humidity, VSBY is
  the visibility, SKNT is the wind speed in knots and GUST is the wind gust in knots. 
  
  <p>A warning event may be listed multiple times, if the UGC zones associated 
  with the warning had different expiration times.
    
  <form method="GET">
  
  <p>
  <table cellpadding='3' cellspacing='0' border='1'>
  <tr>
    <th>WWA Type:</th>
    <th>Start Event ID:</th>
    <th>End Event ID:</th>
    <th>Select WFO:</th>
  	<th>Select Year:</th>
  	</tr>
  	<tr>
  	<td><select name="mode">
  	<option value="BZ.W" <?php if ($mode == "BZ.W") echo "SELECTED='SELECTED';"?>>Blizzard Warning BZ.W</option>
  	<option value="FG.Y" <?php if ($mode == "FG.Y") echo "SELECTED='SELECTED';"?>>Dense Fog Advisory FG.Y</option>
  	<option value="FW.W" <?php if ($mode == "FW.W") echo "SELECTED='SELECTED';"?>>Red Flag Warning FW.W</option>
  	<option value="HW.W" <?php if ($mode == "HW.W") echo "SELECTED='SELECTED';"?>>High Wind Warning HW.W</option>
  	</select></td>
  	<td><input type="text" size="10" name="sid" value="<?php echo $sid; ?>" /></td>
  	<td><input type="text" size="10" name="eid" value="<?php echo $eid; ?>" /></td>
  	<td><?php echo wfoSelect($wfo); ?></td>
    <td><?php echo yearSelect(2005, $year); ?></td>
    </tr>
    </table>
  
  <table cellpadding='3' cellspacing='0' border='1'>
  <tr>	
  	<th>Relative Humidity Threshold (%):</th>
  	<th>Wind Speed Threshold (kts):</th>
  	<th>Visibility Threshold (mile):</th>
    </tr>
    <tr>
    <td><input type="text" size="10" name="relh" value="<?php echo $rhthres; ?>" /></td>
    <td><input type="text" size="10" name="sknt" value="<?php echo $skntthres; ?>" /></td>
    <td><input type="text" size="10" name="vsby" value="<?php echo $vsbythres; ?>" /></td>
    </tr>
    </table>
    <input type="submit" value="Generate Report"/>
  </form>
  
  <?php
  $postgis = iemdb("postgis");
  $asos = iemdb("asos");
  pg_query($postgis, "SET TIME ZONE 'GMT'");
  pg_query($asos, "SET TIME ZONE 'GMT'");
  
  $rs = pg_prepare($asos, "SELECT", "");
  
  $rs = pg_prepare($postgis, "FIND", "SELECT array_to_string(array_accum(ugc),',')
  		as a, eventid, issue, expire from
  		warnings_$year WHERE wfo = $1 and phenomena =  $4 and
  		significance = $5 and eventid >= $2 and eventid < $3 
  		GROUP by issue, expire, eventid ORDER by issue ASC");
  
  $station2ugc = Array();
  $ugc2station = Array();
  $rs = pg_prepare($postgis, "STATIONS", "SELECT id, ugc_zone from stations
  		where wfo = $1 and (network ~* 'ASOS' or network = 'AWOS')");
  $rs = pg_execute($postgis, "STATIONS", Array($wfo));
  for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
  	if (! array_key_exists($row["ugc_zone"], $ugc2station)){
  		$ugc2station[$row["ugc_zone"]] = Array();
  	}
  	$ugc2station[$row["ugc_zone"]][] = $row["id"];
  	$station2ugc[$row["id"]] = $row["ugc_zone"];
  }
  $rs = pg_execute($postgis, "FIND", Array($wfo, $sid, $eid, $phenomena, $significance));

  function c1($relh){
  	global $rhthres;
  	if ($relh >= $rhthres){
  		return sprintf("%.0f%%", $relh);
  	}
  	return sprintf("<span style='color:#f00;'>%.0f%%</span>", $relh);
  }
  function c2($sknt, $gust){
  	global $skntthres;
  	if ($sknt < $skntthres){
  		return sprintf("%s/%sKT", $sknt, $gust);
  	}
  	return sprintf("<span style='color:#f00;'>%s/%sKT</span>", $sknt, $gust);
  }
  function c3($vsby){
	if ($vsby == null) return "MMSM";
  	global $vsbythres;
  	if ($vsby <= $vsbythres){
		return sprintf("<span style='color:#f00;'>%.1fSM</span>", $vsby);
  	}
  	return sprintf("%.1fSM", $vsby);		   
  }
  
  for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
  		$ar = explode(",", $row["a"]);
  		$issue = $row["issue"];
  		$expire = $row["expire"];
  		$eventid = $row["eventid"];
  		$stations = "(";
  		
  		echo sprintf("<h3>Event: %s Issue: %s Expire: %s</h3>\n", $eventid,
  				$issue, $expire);	
  		echo "<p><strong>UGC Codes:</strong> ";
  		while (list($k,$zone)=each($ar)){
  			echo " $zone,";
  			if (array_key_exists($zone, $ugc2station)){
  				reset($ugc2station[$zone]);
  			while (list($k2,$st)=each($ugc2station[$zone])){
  				$stations  .= sprintf("'%s',", $st);
  			}
  			}
  		}
  		$stations .= "'ZZZZZ')";
  		echo "<p><strong>ASOS/AWOS IDs:</strong> ";
  		echo str_replace(",'ZZZZZ'", "", $stations);
  		echo "<br />";
  		$rs2 = pg_query($asos, "SELECT station, valid, to_char(valid, 'ddHH24MI') as z,
  				tmpf, dwpf, sknt, gust, vsby from alldata
  		WHERE valid BETWEEN '$issue' and '$expire' and station in $stations
  				ORDER by station, valid ASC");
  		echo "<table cellpadding='3' cellspacing='0' border='1'>";
  		$ostation = "";
  		$stfound = 0;
  		for($j=0;$row2=@pg_fetch_assoc($rs2,$j);$j++){
  			if ($ostation != $row2["station"]){
  				if ($stfound > 0 && $stfound % 3 == 0){
  					echo "</td></tr>";
  					$ostation = "";
  				}
  				if ($ostation == "") echo "<tr><td valign='top'>";
  				else echo "</td><td valign='top'>";
  				$ostation = $row2["station"];
  				$stfound += 1;
  				echo sprintf("<u>UGC Code: %s</u><br/>", $station2ugc[$row2["station"]]);
  			}
  			echo sprintf("%s %sZ %.0f/%.0f %s %s %s<br>", $row2["station"], 
  					$row2["z"],
  				$row2["tmpf"], $row2["dwpf"], c1(relh($row2["tmpf"], $row2["dwpf"])),
  					c3($row2["vsby"]), c2($row2["sknt"], $row2["gust"]));
  		}
  		echo "</td></tr></table>";
  		
  }
  
  ?>

<?php include("$rootpath/include/footer.php"); ?>
