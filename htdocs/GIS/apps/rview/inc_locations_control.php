<div id="locations-control" style="width: 450px; background: #F2FE5A; display: none; z-index: 3; position: absolute;  padding: 5px; margin: 2px; border: 2px solid #000;">
<strong>NWS Office:</strong><br />
<select name="site" style="width: 195px;">
<?php
while( list($key, $value) = each($wfos) ){
  echo "<option value=\"$key\" ";
  if ($site == $key) echo "SELECTED";
  echo ">[".$key."] ". $wfos[$key]["city"] ."</option>";
}
?>
</select>

<br />Selecting a different office will move the display to that office.
<div style="float: right;"><input type="submit" onClick="javascript: setLayerDisplay('locations-control', 'none'); return false;" value="Save Settings"><input type="submit" value="Save + Update Map"> </div>
</div>
