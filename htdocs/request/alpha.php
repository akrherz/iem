<?php
 $station = 'OT0015';
 require_once "../../config/settings.inc.php";
 require_once "../../include/mlib.php";
   $jdata = file_get_contents("http://iem.local/api/1/currents.json?station=$station");
   $jobj = json_decode($jdata, $assoc=TRUE);
   $ob = $jobj["data"][0];

	 if (isset($_REQUEST['test'])){

	 header('Content-type: text/xml');
 $tstamp = date("M j Y, j:i a T", strtotime($ob["local_valid"]));
 $tstamp2 = date("D, d M Y h:i:00 P", strtotime($ob["local_valid"]));
 $tmpc = f2c($ob["tmpf"]);
 $dwpc = f2c($ob["dwpf"]);
 $tstring = sprintf("%.1f F (%.1f C)", $ob["tmpf"], f2c($ob["tmpf"]));
 $dstring = sprintf("%.1f F (%.1f C)", $ob["dwpf"], f2c($ob["dwpf"]));
 $wstring = sprintf("%s at %.1f MPH (%.1f KT)",
    drct2txt($ob["drct"]), $ob["sknt"] * 1.15, $ob["sknt"]);
$wdirtext = drct2txt($ob["drct"]);
$speed = sprintf("%.1f", $ob["sknt"] * 1.15);
$pres = sprintf("%.2f", $ob['alti'] * 33.86);

 echo <<<EOM
<?xml version="1.0" encoding="ISO-8859-1"?> 
<?xml-stylesheet href="latest_ob.xsl" type="text/xsl"?>
<current_observation version="1.0"
	 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
	 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	 xsi:noNamespaceSchemaLocation="http://www.weather.gov/view/current_observation.xsd">
	<credit>NOAA's National Weather Service</credit>
	<credit_URL>http://weather.gov/</credit_URL>
	<image>
		<url>http://weather.gov/images/xml_logo.gif</url>
		<title>NOAA's National Weather Service</title>
		<link>http://weather.gov</link>
	</image>
	<suggested_pickup>0 minutes after the hour</suggested_pickup>
	<suggested_pickup_period>1</suggested_pickup_period>
	<location>Jefferson, Jefferson Municipal Airport, IA</location>
	<station_id>OT0015</station_id>
	<latitude>42.0131</latitude>
	<longitude>-94.3439</longitude>
  <observation_time>Last Updated on {$tstamp}</observation_time>
  <observation_time_rfc822>{$tstamp2}</observation_time_rfc822>
	<weather>Unknown</weather>
	<temperature_string>${tstring}</temperature_string>
	<temp_f>${ob["tmpf"]}</temp_f>
	<temp_c>${tmpc}</temp_c>
	<relative_humidity>${ob["relh"]}</relative_humidity>
	<wind_string>${wstring}</wind_string>
	<wind_dir>${wdirtext}</wind_dir>
	<wind_degrees>${ob["drct"]}</wind_degrees>
	<wind_mph>${speed}</wind_mph>
	<wind_kt>${ob["sknt"]}</wind_kt>
	<pressure_string>${pres} mb</pressure_string>
	<pressure_mb>${pres}</pressure_mb>
	<pressure_in>${ob["alti"]}</pressure_in>
	<dewpoint_string>${dstring}</dewpoint_string>
	<dewpoint_f>${ob["dwpf"]}</dewpoint_f>
	<dewpoint_c>$dwpc</dewpoint_c>
	<visibility_mi>Unknown</visibility_mi>
 	<icon_url_base>http://forecast.weather.gov/images/wtf/small/</icon_url_base>
	<two_day_history_url>http://www.weather.gov/data/obhistory/KAMW.html</two_day_history_url>
	<icon_url_name>few.png</icon_url_name>
	<ob_url>http://www.weather.gov/data/METAR/KAMW.1.txt</ob_url>
	<disclaimer_url>http://weather.gov/disclaimer.html</disclaimer_url>
	<copyright_url>http://weather.gov/disclaimer.html</copyright_url>
	<privacy_policy_url>http://weather.gov/notice.html</privacy_policy_url>
</current_observation>
EOM;
die();
}

header('Content-type: text/plain');
 echo intval($ob["tmpf"]) ."\n";
 echo intval($ob["dwpf"]) ."\n";
 echo intval($ob["sknt"]) ."\n";
 echo drct2txt($ob["drct"]) ."\n";
 echo round(max($ob["gust"], $ob["sknt"]),0) ."\n";
 echo $ob["pday"] ."\n";
 echo $ob["relh"] ."\n";
 echo $ob["alti"] ."\n";
 echo intval($ob["feel"]) ."\n";
