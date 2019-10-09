<?php 
require_once '../config/settings.inc.php';
include("../include/database.inc.php");
//$dbconn = iemdb("mesosite");
$dbconn = pg_connect("dbname=mesosite host=iemdb-mesosite.local");

$rs = pg_prepare($dbconn, "ADDSUB", "INSERT into iembot_room_subscriptions
                 (roomname, channel) VALUES ($1,$2)");
$rs = pg_prepare($dbconn, "DELSUB", "DELETE from iembot_room_subscriptions
				WHERE roomname = $1 and channel = $2");
$rs = pg_prepare($dbconn, "SELECTSUBS", "SELECT c.* from
                 iembot_room_subscriptions s, iembot_channels c
                 WHERE s.roomname = $1 and c.id = s.channel 
                 ORDER by channel ASC");
$rs = pg_prepare($dbconn, "SELECTCHANNELS", "SELECT * from
                 iembot_channels WHERE id NOT IN
                   (SELECT channel from
                    iembot_room_subscriptions WHERE roomname = $1)
                 and id ~* $2
                 ORDER by id ASC LIMIT $3 OFFSET $4");


if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "remove"){
	pg_execute($dbconn, "DELSUB", Array($_REQUEST["chatroom"],
									$_REQUEST["channel"]));
	die(0);
}
if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "add"){
	pg_execute($dbconn, "ADDSUB", Array($_REQUEST["chatroom"],
									$_REQUEST["channel"]));
	die(0);
}

if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "subs"){
	$rs = pg_execute($dbconn, "SELECTSUBS", Array($_REQUEST["chatroom"]));
	$total = pg_num_rows($rs);
}
else {
	$rs = pg_execute($dbconn, "SELECTCHANNELS", Array($_REQUEST["chatroom"],
							$_REQUEST["query"], $_REQUEST["limit"],
							$_REQUEST["start"]));
	$rs2 = pg_execute($dbconn, "SELECTCHANNELS", Array($_REQUEST["chatroom"],
							$_REQUEST["query"], 100000, 0));
	$total = pg_num_rows($rs2);					
}
$ar = Array("channels" => Array() , "totalCount" => $total);

for ($i=0;$row=@pg_fetch_array($rs, $i);$i++){
	$z = Array("id" => $row["id"], "text" => $row["name"]);
	$ar["channels"][] = $z;
}

echo json_encode($ar);
?>
