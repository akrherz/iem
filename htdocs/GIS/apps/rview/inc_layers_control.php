<strong>Realtime Only Layers</strong>
<br /><input name="layers[]" type="checkbox" value="usdm" <?php if (in_array("usdm", $layers)) echo "checked='CHECKED'"; ?>>US Drought Monitor
<br /><input name="layers[]" type="checkbox" value="goes_east1V" <?php if (in_array("goes_east1V", $layers)) echo "checked='CHECKED'"; ?>>GOES East Visible
<br /><input name="layers[]" type="checkbox" value="goes_west1V" <?php if (in_array("goes_west1V", $layers)) echo "checked='CHECKED'"; ?>>GOES West Visible
<br /><input name="layers[]" type="checkbox" value="goes_east04I4" <?php if (in_array("goes_east04I4", $layers)) echo "checked='CHECKED'"; ?>>GOES East IR
<br /><input name="layers[]" type="checkbox" value="goes_west04I4" <?php if (in_array("goes_west04I4", $layers)) echo "checked='CHECKED'"; ?>>GOES West IR
<br /><strong>Layers</strong>
<br /><input name="layers[]" type="checkbox" value="nexrad" <?php if (in_array("nexrad", $layers)) echo "checked='CHECKED'"; ?>>US NEXRAD
<br /><input name="layers[]" type="checkbox" value="warnings" <?php if (in_array("warnings", $layers)) echo "checked='CHECKED'"; ?>>Warnings
<img src="static/warnings_legend.png" style="margin-left: 20px;">
<br /><input name="layers[]" type="checkbox" value="watches" <?php if (in_array("watches", $layers)) echo "checked='CHECKED'"; ?>>Watches
<input type="hidden" name="layers[]" value="blank">
<br /><input name="layers[]" type="checkbox" value="cwas" <?php if (in_array("cwas", $layers)) echo "checked='CHECKED'"; ?>>WFO Boundaries
<br /><input name="layers[]" type="checkbox" value="uscounties" <?php if (in_array("uscounties", $layers)) echo "checked='CHECKED'"; ?>>US Counties
