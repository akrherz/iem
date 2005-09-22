<?php
$TITLE = "IEM | Help Window Test Page";
include("/mesonet/php/include/header.php"); ?>
<script LANGUAGE="JavaScript1.2" type="text/javascript">
//

<!--
function setLayerDisplay( layerName, d ) {   if ( document.getElementById ) {     var w = document.getElementById(layerName);     w.style.display = d;   }
}
-->
</script>
<h3 class="heading">IEM Help Window Test Page</h3><br><br>

<input type="submit" value="Help Me!" onclick="javascript: setLayerDisplay('helpwindow', 'block'); return false;">


<div class="text"><p>Climatology can help us answer questions like: What
happened yesterday?, What happened last week?, and What is normal for this
period?. This page contains answers to some of these questions using IEM
data.Check out the Iowa State Climatologist's page for more info.<br><br>

<div id="helpwindow" style="display: none;">
<h3 class="subtitle">Help:</h3> This is where the help window appears. (<a href="javascript: setLayerDisplay('helpwindow', 'none');">Close</a>)</div>
</div>

<?php include("/mesonet/php/include/footer.php"); ?>
