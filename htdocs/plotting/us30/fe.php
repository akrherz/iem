<html>
<head>
  <title>US 30 Comparison</title>
</head>

<body bgcolor="white">

<?php if (strlen($param) > 0){
   echo "<img src=\"plot1.php?mode=".$mode."&date1=".$date1."&date2=".$date2."&st1=".$st1."&st2=".$st2."&param=".$param."\">";
  } else { 
?>

<form method="GET" action="fe.php" target="display">

<table>
<tr>

<td>
<p>Select Parameter:
<br><select name="param">
 <option value="tmpf">Temperature
 <option value="dwpf">Dew Point
 <option value="sknt">Wind Speed
</select>
</td>

<td>
<p>Station 1:
<br><select name="st1">
  <option value="amw">Ames ASOS
  <option value="campbell">DOT Campbell Station
  <option value="rame">Ames RWIS
  <option value="sboo">Boone SchoolNet
  <option value="bnw">Boone AWOS
  <option value="isu0209">Ames Farm Campbell
  <option value="ames_scan">Ames SCAN Site
</select>
</td>

<td>
<p>Station 2:
<br><select name="st2">
  <option value="amw">Ames ASOS
  <option value="campbell">DOT Campbell Station
  <option value="rame">Ames RWIS
  <option value="sboo">Boone SchoolNet
  <option value="bnw">Boone AWOS
  <option value="isu0209">Ames Farm Campbell
  <option value="ames_scan">Ames SCAN Site
</select>
</td>
</tr>

<tr>
<td>
<p>Begin Date:
<br><input type="text" name="date1" size="20">
<br>(yyyy-mm-dd)
</td>

<td>
<p>End Date:
<br><input type="text" name="date2" size="20">
<br>(yyyy-mm-dd)
</td>

<td>
<p>Mode:
<br><select name="mode">
 <option value="diff">Difference Plot
 <option value="side">Side by Side
</select>
</td>

</tr>
</table>

<p>Submit:
<br><input type="submit" value="Create Plot">


</form>

<?php } ?>

</body>
</html>
