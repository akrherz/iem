<?php
 include("../../../config/settings.inc.php");
?>
<html>
<head>
 <title>Top</title>
</head>
<body bgcolor="white">

<form method="GET" action="retreive.php" target="display">

<table border="0" width="100%">
<tr>
  <th>Enter AFOS PIL:<br>
  ex) <i>AFDDMX</i></th> 
  <td><input type="text" name="pil" size=20></td>

  <td><SELECT name="cnt">
	<option value="1">Latest
	<option value="2">Last 2
	<option value="5">Last 5
	<option value="10">Last 10
	<option value="1500">Last 1500
</SELECT></td>

  <td><input type="submit" value="GET"></td>

  <td valign="top" align="right"><b><a target="display" href="bottom.php">NWS Text Product Finder</a></b><br>
  <a target="_top" href="/">Iowa Environmental Mesonet</a><br>
  <b>*</b>Unofficial data for educational use only.

</tr></table>

</form>
</body>
</html>
