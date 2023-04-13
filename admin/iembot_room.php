<?php
/* Controller for NWSBot stuff in rooms
 * 
 */ 
require_once '../config/settings.inc.php';
require_once "../include/database.inc.php";
$dbconn = iemdb("mesosite");

$rs = pg_prepare($dbconn, "CREATEROOM", "insert into nwsbot_rooms
                 (roomname, logemail, logmode)
                 values ($1, $2, $3)");


if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "join"){
    pg_execute($dbconn, "DELSYND", Array($_REQUEST["chatroom"],
                                    $_REQUEST["synd"]));
    die(0);
}
if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "add"){
    pg_execute($dbconn, "ADDSYN", Array($_REQUEST["synd"],
                                    $_REQUEST["chatroom"], 'P'));
    die(0);
}

if (isset($_REQUEST["mode"]) && $_REQUEST["mode"] == "subs"){
    $rs = pg_execute($dbconn, "SYNROOMS", Array($_REQUEST["chatroom"]));
    $total = pg_num_rows($rs);
}
else {
    $rs = pg_execute($dbconn, "SELECTROOMS", Array($_REQUEST["chatroom"],
                            $_REQUEST["query"], $_REQUEST["limit"],
                            $_REQUEST["start"]));
    $rs2 = pg_execute($dbconn, "SELECTROOMS", Array($_REQUEST["chatroom"],
                            $_REQUEST["query"], 100000, 0));
    $total = pg_num_rows($rs2);					
}
$ar = Array("synd" => Array() , "totalCount" => $total);

for ($i=0;$row=pg_fetch_array($rs);$i++){
    $z = Array("id" => $row["roomname"], "text" => $row["roomname"]);
    $ar["synd"][] = $z;
}

echo json_encode($ar);
