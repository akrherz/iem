<?php
include("../../../include/forms.php");
if (! isset($year) ) $year = 2003;
if (! isset($month) ) $month = 5;
if (! isset($day) ) $day = 4;
?>
<table border=1><tr><td>
<form method="GET" action="township.phtml">
<input type="hidden" value="<?php echo $twp; ?>" name="twp">
<input type="hidden" value="2003" name="year">
<table>
<tr>
 <td>Select Month:</td><td><?php monthSelect($month, "month"); ?></td>
</tr><tr>
 <td>Select Day:</td><td><?php daySelect($day, "day"); ?></td>
</tr>
</table>
<input type="submit" value="Select Date">
</form>
</td></tr></table>
