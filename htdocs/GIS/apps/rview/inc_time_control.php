<div id="time-control" style="width: 450px; background: #FF5EC4; display: none; z-index: 3; position: absolute;  padding: 5px; margin: 2px; border: 2px solid #000;">
<p><strong>Select Time Zone</strong><br />
<select name="tz">
  <option value="UTC" <?php if ($tz == "UTC") echo "SELECTED"; ?>>UTC
  <option value="EDT" <?php if ($tz == "EDT") echo "SELECTED"; ?>>EDT
  <option value="EST" <?php if ($tz == "EST") echo "SELECTED"; ?>>EST
  <option value="CDT" <?php if ($tz == "CDT") echo "SELECTED"; ?>>CDT
  <option value="CST" <?php if ($tz == "CST") echo "SELECTED"; ?>>CST
  <option value="MDT" <?php if ($tz == "MDT") echo "SELECTED"; ?>>MDT
  <option value="MST" <?php if ($tz == "MST") echo "SELECTED"; ?>>MST
  <option value="PDT" <?php if ($tz == "PDT") echo "SELECTED"; ?>>PDT
  <option value="PST" <?php if ($tz == "PST") echo "SELECTED"; ?>>PST
</select>

<p><strong>Archive Options</strong><br />
<input type="checkbox" value="yes" name="archive" <?php if($isarchive) echo
"CHECKED=CHECKED"; ?>>Set Archive Mode</td>
<table cellpadding="2" cellspacing="0" border="0">
<tr><th>Year:</th><td><?php echo yearSelect(2003, $year, "year"); ?></td></tr>
<tr><th>Month:</th><td><?php echo monthSelect($month, "month"); ?></td></tr>
<tr><th>Day:</th><td><?php echo daySelect($day, "day"); ?></td></tr>
<tr><th>Time:</th><td><?php echo hourSelect($hour, "hour"); ?>:<?php echo minuteSelect($m, "minute",5); ?></td></tr>
</table>

<p><div style="float: right;"><input type="submit" onClick="javascript: setLayerDisplay('time-control', 'none'); setLayerDisplay('applet-hack', 'block'); return false;" value="Save Settings"><input type="submit" value="Save + Update Map"> </div>
</div>
