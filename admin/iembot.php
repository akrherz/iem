<?php
include("../config/settings.inc.php");
include("Zend/XmlRpc/Client.php");
include("$rootpath/include/database.inc.php");
//$dbconn = iemdb("mesosite");
$dbconn = pg_connect("dbname=mesosite");

$rs = pg_prepare($dbconn, "SELECTROOMS", "SELECT * from iembot_rooms 
                 WHERE roomname NOT IN ('allpeopletalk', 'botstalk')
                 ORDER by roomname ASC");
$rs = pg_prepare($dbconn, "SELECTROOM", "SELECT * from iembot_rooms
                 WHERE roomname = $1");
$rs = pg_prepare($dbconn, "CREATEROOM", "insert into iembot_rooms
                 (roomname) values ($1)");
$rs = pg_prepare($dbconn, "DELETEROOM", "DELETE from iembot_rooms WHERE
                 roomname = $1");
$rs = pg_prepare($dbconn, "DELETESUBS", "DELETE from iembot_room_subscriptions
                 WHERE roomname = $1"); 

$room = isset($_REQUEST["room"]) ? $_REQUEST["room"]: "";
$channel = isset($_REQUEST["channel"]) ? $_REQUEST["channel"]: "";
$action = isset($_REQUEST["action"]) ? $_REQUEST["action"]: "";
$sub = isset($_REQUEST["sub"]) ? $_REQUEST["sub"]: Array();

function reloadbot(){
	$alertMsg = file_get_contents("http://localhost/iembot-json/reload");
}


if ($action == "delete" && $room != ""){
  pg_execute($dbconn, "DELETEROOM", Array($room));
  pg_execute($dbconn, "DELETESUBS", Array($room));
  reloadbot();
  $alertMsg = "Deleted roomname ($room) and reloaded iembot";
}

if ($action == "add" && $room != ""){
  /* Add a new room to the bot! */
  pg_execute($dbconn, "CREATEROOM", Array($room));
  reloadbot();
  $alertMsg = "Created roomname ($room) and reloaded iembot";
}


/* BEGIN WEB OUTPUT PLEASE */
$HEADEXTRA = '<link rel="stylesheet" type="text/css" 
	href="https://nwschat.weather.gov/ext-3.4.0/resources/css/ext-all.css"/>
<script type="text/javascript" src="https://nwschat.weather.gov/ext-3.4.0/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="https://nwschat.weather.gov/ext-3.4.0/ext-all.js"></script>
<script type="text/javascript">
Ext.ns("App");
App.roomname = "'. $room .'";
</script>
<style>
.search-item {
    font:normal 11px tahoma, arial, helvetica, sans-serif;
    padding:3px 10px 3px 10px;
    border-bottom:1px solid #eeeeee;
}
.search-item h3 {
    display:block;
    font:inherit;
    font-weight:bold;
}

.search-item h3 span {
    float: right;
    font-weight:normal;
    margin:0 0 5px 5px;
    width:100px;
    display:block;
    clear:none;
}
</style>
';
include("$rootpath/include/header.php");
?>
<h3>IEMBot Chatroom Configuration Page</h3>
<?php
if (isset($alertMsg)){ 
  echo "<div class=\"warning\">$alertMsg</div>";
}

if ($room != "" && $action != "delete"){
  echo "<div style=\"border: 3px solid #000; background: #eee; padding:20px;\">";

  echo "<p><strong>Please click the 'Update Room Settings' once done</strong><br />
    <table width=\"800\"><tr><td width=\"400\">
    <div class=\"x-box-tl\"><div class=\"x-box-tr\"><div class=\"x-box-tc\"></div></div></div>
    <div class=\"x-box-ml\"><div class=\"x-box-mr\"><div class=\"x-box-mc\">
        <div style=\"padding-top:4px;\">
            <h3>Current Channel Subscriptions:</h3>
        </div>
	    <div style=\"padding-top:4px;\">
            Click in list to remove.
        </div>
	
       <div id=\"channel_del\" /></div>
        
        <div style=\"padding-top:4px;\">
            Enter some text to search for channels.
        </div>
		<input type=\"text\" size=\"20\" name=\"channelsearch\" 
		id=\"channelsearch\" />

    </div></div></div>
    <div class=\"x-box-bl\"><div class=\"x-box-br\"><div class=\"x-box-bc\"></div></div></div>
</div>
    </td><td width=\"400\">

    </td></tr></table>
 
        <script src=\"iembot.js\" type=\"text/javascript\">
        </script>";
  
  

  echo "<h4><img src=\"../images/configure.png\"/> Edit room settings for: ${room}</h4>";

  echo sprintf("<a href=\"iembot.php?action=delete&room=%s\">Click to remove iembot from %s room</a>", $room, $room);

  echo "<form name=\"modify\" method=\"POST\">";
  echo "<input type=\"hidden\" name=\"action\" value=\"modify\">";
  echo "<input type=\"hidden\" name=\"room\" value=\"${room}\">";
  $rs = pg_execute($dbconn, "SELECTROOM", Array($room));
  $row = pg_fetch_array($rs,0);
  echo "<p><strong>Email daily logfile to (comma delimited):</strong><br />
       <input size=\"80\" type=\"text\" name=\"email\" value=\"". $row["logemail"] ."\">";

  echo "<p><strong>Associated Facebook Page ID (numeric):</strong><br />" .
  		"<input type=\"text\" name=\"fbpage\" value=\"". $row["fbpage"] ."\" />";
  echo "<p><strong>Associated Twitter Account (string):</strong><br />" .
  		"<input type=\"text\" name=\"twitter\" value=\"". $row["twitter"] ."\" />";

  echo "<p><strong>Email Log Mode:</strong><br />
       <select name=\"logmode\">";
  echo "<option value=\"1\" ";
  if ($row["logmode"] == 1) echo "SELECTED";
  echo ">Exclude NWSBot Messages</option>";
  echo "<option value=\"2\" ";
  if ($row["logmode"] == 2) echo "SELECTED";
  echo ">Only NWSBot Messages</option>";
  echo "<option value=\"3\" ";
  if ($row["logmode"] == 3) echo "SELECTED";
  echo ">All Messages</option>";

  echo "</select>";

  echo "<p><strong>Room registration via the web:</strong><br />
       <input type=\"checkbox\" name=\"webreg\" value=\"yes\" ";
  if ($webreg == 't') { echo "checked=\"checked\""; } 
  echo "> Allow this functionality?<br />
       <a href=\"${rooturl}/my/join_chatroom.php?key=". $row["register_key"] ."\">${rooturl}/my/join_chatroom.php?key=". $row["register_key"] ."</a>";


  echo "<p><input type=\"submit\" value=\"Update Room Settings\">";
  echo "</form>";
  echo "</div>";
  reloadbot();
}
?>

<h4>Option 1: Enter room name for iembot to join</h4>
<div style="padding-left: 20px;">
<form name="add" method="GET">
<input type="hidden" name="action" value="add">
<p><strong>Enter Roomname:</strong><input type="text" name="room">
<p><strong>Email address where to send daily logs of people talking?:</strong> <input type="text" name="email"> (may be left blank)
<p><input type="submit" value="Create Room">
</form>
</div>

<h4>Option 2: Create a Channel</h4>
<div style="padding-left: 20px;">
<form name="addchannel" method="GET">
<input type="hidden" name="action" value="addchannel">
<p><strong>Enter Channel ID:</strong><input type="text" name="channel">
<p><strong>Email optional name:</strong> <input type="text" name="name"> (may be left blank)
<p><input type="submit" value="Create Channel">
</form>
</div>


<h4>Option 3: Edit a room's settings</h4>
<div style="padding-left: 20px;">
<table>
<?php
$rs = pg_execute($dbconn, "SELECTROOMS", Array());
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  if ($i % 8 == 0) echo "</tr><tr>";
  echo sprintf("<td><a href=\"iembot.php?action=edit&room=%s\">%s</a></td>",
               $row["roomname"], $row["roomname"] );
}
?>
</tr></table>

</div>



<?php include("$rootpath/include/footer.php"); ?>
