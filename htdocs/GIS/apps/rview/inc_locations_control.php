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
