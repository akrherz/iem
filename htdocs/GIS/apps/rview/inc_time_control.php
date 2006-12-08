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
<tr><th>Time:</th><td><?php echo hourSelect($hour, "hour"); ?>:<?php echo local5MinuteSelect($m, "minute"); ?></td></tr>
</table>

<p>
