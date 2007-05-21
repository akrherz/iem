<div id="layers-control" style="width: 450px; background: #73FA4D; display: none; z-index: 3; position: absolute; padding: 5px; margin: 2px; border: 2px solid #000;">

<strong>Realtime Only Layers</strong>
<br /><input name="layers[]" type="checkbox" value="usdm" <?php if (in_array("usdm", $layers)) echo "checked='CHECKED'"; ?>>US Drought Monitor
<br /><input name="layers[]" type="checkbox" value="goes_east1V" <?php if (in_array("goes_east1V", $layers)) echo "checked='CHECKED'"; ?>>GOES East Visible
<br /><input name="layers[]" type="checkbox" value="goes_west1V" <?php if (in_array("goes_west1V", $layers)) echo "checked='CHECKED'"; ?>>GOES West Visible
<br /><input name="layers[]" type="checkbox" value="goes_east04I4" <?php if (in_array("goes_east04I4", $layers)) echo "checked='CHECKED'"; ?>>GOES East IR
<br /><input name="layers[]" type="checkbox" value="goes_west04I4" <?php if (in_array("goes_west04I4", $layers)) echo "checked='CHECKED'"; ?>>GOES West IR
<br /><input name="layers[]" type="checkbox" value="current_barbs" <?php if (in_array("current_barbs", $layers)) echo "checked='CHECKED'"; ?>>Current Wind Barbs
<br /><input name="layers[]" type="checkbox" value="airtemps" <?php if (in_array("airtemps", $layers)) echo "checked='CHECKED'"; ?>>Current Air Temps
<br /><input name="layers[]" type="checkbox" value="current_sites" <?php if (in_array("current_sites", $layers)) echo "checked='CHECKED'"; ?>>Site Labels
<br /><strong>Layers</strong>
<br /><input name="layers[]" type="checkbox" value="nexrad" <?php if (in_array("nexrad", $layers)) echo "checked='CHECKED'"; ?>>US NEXRAD
<br /><input name="layers[]" type="checkbox" value="warnings" <?php if (in_array("warnings", $layers)) echo "checked='CHECKED'"; ?>>Warnings

<br /><input name="layers[]" type="checkbox" value="watches" <?php if (in_array("watches", $layers)) echo "checked='CHECKED'"; ?>>Watches
<input type="hidden" name="layers[]" value="blank">
<br /><input name="layers[]" type="checkbox" value="cwas" <?php if (in_array("cwas", $layers)) echo "checked='CHECKED'"; ?>>WFO Boundaries
<br /><input name="layers[]" type="checkbox" value="uscounties" <?php if (in_array("uscounties", $layers)) echo "checked='CHECKED'"; ?>>US Counties
<br /><input name="layers[]" type="checkbox" value="interstates" <?php if (in_array("interstates", $layers)) echo "checked='CHECKED'"; ?>>US Interstates

<div style="float: right;"><input type="submit" onClick="javascript: setLayerDisplay('layers-control', 'none'); setLayerDisplay('applet-hack', 'block'); return false;" value="Save Settings"><input type="submit" value="Save + Update Map"> </div>
</div>
