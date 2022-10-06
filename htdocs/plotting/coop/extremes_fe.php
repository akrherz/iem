<?php 
require_once "../../../config/settings.inc.php";
include_once "../../../include/myview.php";
include_once "../../../include/imagemaps.php";
require_once "../../../include/forms.php";
$t = new MyView();
$t->title = "COOP Extremes Plots";
$station = isset($_GET["station"]) ? xssafe($_GET["station"]): ""; 
$var = isset($_GET["var"]) ? xssafe($_GET["var"]): "";

$nselect = networkSelect("IACLIMATE", $station);

$ar = Array("high" => "High Temperature", "low" => "Low Temperature");
$varselect = make_select("var", $var, $ar);

$imgurl = "";
if (strlen($station) > 0 ){
    $imgurl = "<img src=\"extremes.php?var=". $var ."&amp;station=". $station ."\">\n";
}


$t->content = <<<EOF
<ol class="breadcrumb">
<li><a href="/">IEM</a></li>
<li><a href="/climate/">Climatology</a></li>
<li class="active">COOP Daily Extremes</li>
</ol>

<BR>
<p>Using the NWS COOP dataset, the IEM has calculated daily
temperature extremes.  You can create a annual plot of this dataset for a
station of your choice.</p> 


<form method="GET" action="extremes_fe.php">

<table>
<tr>
  <th class="subtitle">Station</th>
  <th class="subtitle">Variable</th>
  <td></td>
</tr>

<tr>
<td>{$nselect}</td>
<td>{$varselect}</td>
<td>
<input type="submit" value="Make Plot">

</form>
</td>

</tr></table>

{$imgurl}
EOF;
$t->render('single.phtml');
