<?php
/* scenario.inc.php
 *  - Storm Scenario
 */


class scenario {

function scenario($id)
{
	$this->id = $id;
	$this->load();
} // End constructor

function load()
{ // Load values either from database or create new ones
	global $basins, $pg;
	$this->data = Array();
	$this->newstorm = true;
	while (list($basin, $v) = each($basins))
	{
		$this->data[$basin] = Array("precip" => 0, 
			"sts" => time(), "dur" => 1);
	}

	/* Load from the database, if it exists */
	$sql = "SELECT * from scenario_events e, scenarios s WHERE e.scenario_id = s.id 
		and e.scenario_id = ". $this->id ;
	$rs = pg_query($pg, $sql);

	while($row = pg_fetch_array($rs))
	{
		$this->newstorm = false;
		$this->notes = $row["notes"];
		$this->name = $row["name"];
		$this->data[ $row["basin_id"] ] = Array("precip" => $row["precip"],
			"sts" => strtotime(substr($row["onset"],0,16)), "dur" => $row["duration"]);
	}
} // End of load()


function htmlEditor()
{
	global $basins;
	$s = '
		<input type="hidden" value="'. $this->id .'" name="id">
<p><b>Name of Storm Event:</b> <input type="text" name="name" value="'. $this->name .'">

<script LANGUAGE="JavaScript1.2" type="text/javascript">
//<!--

function setDay()
{
  for (i=0; i<13; i++)
  {
    document.estorm["r_day_"+ i].selectedIndex = document.estorm.gday.selectedIndex;
  }
}

function setHour()
{
  for (i=0; i<13; i++)
  {
    document.estorm["r_hour_"+ i].selectedIndex = document.estorm.ghour.selectedIndex;
  }
}

-->
</script>


<p><b>Date Defaults:</b>
 <br /><i>Modify these items to set all times at once:</i>
<br /><b>Relative Day:</b>
<select name="gday" onchange="javascript: setDay();">
 <option value="0">Day0
 <option value="1">Next Day
 <option value="2">Day 2
</select>

<b>Hour:</b>  
<select name="ghour" onchange="javascript: setHour();">
 <option value="0">Midnight
 <option value="1">1 AM
 <option value="2">2 AM
 <option value="3">3 AM
 <option value="4">4 AM
 <option value="5">5 AM
 <option value="6">6 AM
 <option value="7">7 AM
 <option value="8">8 AM
 <option value="9">9 AM
 <option value="10">10 AM
 <option value="11">11 AM
 <option value="12">Noon
 <option value="13">1 PM
 <option value="14">2 PM
 <option value="15">3 PM
 <option value="16">4 PM
 <option value="17">5 PM
 <option value="18">6 PM
 <option value="19">7 PM
 <option value="20">8 PM
 <option value="21">9 PM
 <option value="22">10 PM
 <option value="23">11 PM
</select>

<p><b>Enter Rainfall Totals:</b>
<table class="ruler">
<thead>
<tr>
        <th>ID:</th>
        <th>Basin:</th>
        <th>Storm Precip:</th>
        <th>Day:</th>
        <th>Hour:</th>
        <th>Duration (hrs):</th>
        </tr>
</thead>
                                                                                
<tbody>
';
	for($i=0;$i<13;$i++)
	{
		$s .= "<tr class=\"row". ($i % 2) ."\"><th>${i}</th>
		 <th>". $basins[$i]["name"] ."</th>
		 <td><input type=\"text\" size=\"5\" name=\"r_stp_${i}\" value=\"". $this->data[$i]["precip"] ."\"></td>
 <td>". dayOffsetSelect( date("d", $this->data[$i]["sts"]) -1, "r_day_${i}") ."</td>
 <td>". localHourSelect(date("G", $this->data[$i]["sts"]), "r_hour_${i}")."</td>
		 <td><input type=\"text\" size=\"5\" name=\"r_dur_${i}\" value=\"". $this->data[$i]["dur"] ."\"></td>
		 </tr>";
	}

	$s .= '</tbody></table>';
	$s .= '<p><b>Notes on event:</b><br>
<textarea name="notes" cols=60 rows=5>'. $this->notes .'</textarea>';

	return $s;	

} // End of htmlEditor()

function initStormEditor()
{
	$this->nextStormID();
	$s = '';
	$s = "<p><b>Storm ID: ". $this->id ." generated.</b>
		<input type=\"hidden\" value=\"". $this->id ."\" name=\"id\">
		<p>Enter Name for this Storm:<input type=\"text\" name=\"name\">";
	return $s;
}

function nextStormID()
{
	global $pg;
	$sql = "SELECT nextval('public.scenarios_id_seq'::text) as id";
	$rs = pg_query($pg, $sql);
	$row = pg_fetch_array($rs);
	$this->id = $row["id"];

}

function processCGI($form)
{
	if (isset($form["name"]) && $this->newstorm)
	{
		$this->name = $form["name"];
		$this->initDB();
		$this->load();
	}

	if (isset($form["r_stp_0"]))
	{ // Work to be done!
		for ($i=0;$i<13;$i++)
		{
			$this->data[$i]["precip"] = $form["r_stp_$i"];
			$this->data[$i]["dur"] = $form["r_dur_$i"];
			$this->data[$i]["sts"] = mktime($form["r_hour_$i"], 0, 0,
				1, 1 + $form["r_day_$i"], 2002);
		}
		$this->notes = $form["notes"];
		$this->name = $form["name"];
		$this->saveData();
	}

} // End of processCGI()

function saveData()
{
	global $pg;

	for($i=0;$i<13;$i++)
	{
		$sql = "UPDATE scenario_events SET precip = ". $this->data[$i]["precip"] .",
			onset = '". strftime("%Y-%m-%d %H:%M", $this->data[$i]["sts"]) ."',
			duration = ". $this->data[$i]["dur"] ." WHERE scenario_id = 
			". $this->id ." and basin_id = $i ";
		pg_query($pg, $sql);
	}
	$sql = "UPDATE scenarios SET edited = now(), notes = '". $this->notes ."'
		, name = '". $this->name ."' WHERE id = ". $this->id ;
	pg_query($pg, $sql);
	$this->message .= "Storm Saved Sucessfully <br />";

} // End of saveData

function initDB()
{
	global $pg;

	$sql = "INSERT into scenarios(id, name, created, edited, notes) VALUES 
		(". $this->id .", '". $this->name ."', now(), now(), '')";
	pg_query($pg, $sql);

	for($i=0;$i<13;$i++)
	{
		$sql = "INSERT into scenario_events(scenario_id, basin_id, precip, onset, duration)
			VALUES (". $this->id .", $i, 0, now(), 1)";
		pg_query($pg, $sql);
	}

}

function delete()
{
	global $pg;

	$sql = "DELETE from scenario_events WHERE scenario_id = ". $this->id ;
	pg_query($pg, $sql);

	$sql = "DELETE from scenarios WHERE id = ". $this->id ;
	pg_query($pg, $sql);


}

} // End of storm

?>
