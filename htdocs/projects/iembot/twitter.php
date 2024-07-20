<?php
session_start();
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 102);
require_once "../../../include/myview.php";
require_once "../../../include/vendor/autoload.php";

use Abraham\TwitterOAuth\TwitterOAuth;

require_once "../../../include/iemprop.php";
require_once "../../../include/forms.php";
require_once "../../../include/database.inc.php";

define("TWITTER_KEY", get_iemprop('bot.twitter.consumerkey'));
define("TWITTER_SECRET", get_iemprop('bot.twitter.consumersecret'));

$pgconn = iemdb('mesosite');
$user_id = isset($_SESSION["user_id"]) ? $_SESSION["user_id"] : '';
$screen_name = isset($_SESSION["screen_name"]) ? $_SESSION["screen_name"] : '';
$channel = isset($_REQUEST["channel"]) ? strtoupper(xssafe($_REQUEST["channel"])) : '';
$channel = trim($channel);

$rs = pg_prepare($pgconn, "SAVEAUTH", "INSERT into " .
    "iembot_twitter_oauth " .
    "(user_id, screen_name, access_token, access_token_secret) " .
    "VALUES ($1,$2,$3,$4)");
$rs = pg_prepare($pgconn, "UPDATEAUTH", "UPDATE iembot_twitter_oauth " .
    "SET access_token = $1, access_token_secret = $2, updated = now(), " .
    "screen_name = $3 WHERE user_id = $4 RETURNING screen_name");

$rs = pg_prepare(
    $pgconn,
    "DELETEAUTH",
    "DELETE from iembot_twitter_oauth where user_id = $1",
);

$rs = pg_prepare($pgconn, "SELECTSUBS", "SELECT * from " .
    "iembot_twitter_subs WHERE user_id = $1 ORDER by channel ASC");
$rs = pg_prepare($pgconn, "ADDSUB", "INSERT into " .
    "iembot_twitter_subs(user_id, screen_name, channel) VALUES ($1, $2, $3)");
$rs = pg_prepare($pgconn, "DELSUB", "DELETE from " .
    "iembot_twitter_subs WHERE user_id = $1 and channel = $2");

$rs = pg_prepare(
    $pgconn,
    "DELETESUBS",
    "DELETE from iembot_twitter_subs where user_id = $1",
);


function reloadbot()
{
    return file_get_contents("http://iembot:9003/reload");
}

$msg = array();
//------------------------------------------------------------
if (isset($_REQUEST["removeme"]) && $_REQUEST["removeme"] == "1") {
    // remove subs first due to foreign key constraints
    pg_execute($pgconn, "DELETESUBS", array($user_id));
    pg_execute($pgconn, "DELETEAUTH", array($user_id));
    $msg[] = "You have been removed from the bot.";
    reloadbot();
    unset($_SESSION["user_id"]);
    unset($_SESSION["screen_name"]);
}
if (isset($_REQUEST['add']) && $channel != '' && $screen_name != '') {
    pg_execute($pgconn, 'ADDSUB', array(
        $_SESSION["user_id"],
        strtolower($_SESSION["screen_name"]), $channel
    ));
    reloadbot();
    $msg[] = sprintf(
        "Added channel subscription %s for user %s, reloaded bot",
        $channel,
        $_SESSION["screen_name"]
    );
}
if (isset($_REQUEST['del']) && $channel != '' && $screen_name != '') {
    pg_execute($pgconn, 'DELSUB', array(
        strtolower($_SESSION["user_id"]),
        $channel
    ));
    reloadbot();
    $msg[] = sprintf(
        "Deleted channel subscription %s for user %s, reloaded bot",
        $channel,
        $_SESSION["screen_name"]
    );
}
if (isset($_REQUEST['cb']) && isset($_SESSION['token']) && isset($_SESSION['token_secret'])) {
    $connection = new TwitterOAuth(
        TWITTER_KEY,
        TWITTER_SECRET,
        $_SESSION['token'],
        $_SESSION['token_secret'],
    );
    $atoken = $connection->oauth(
        "oauth/access_token",
        array("oauth_verifier" => $_REQUEST['oauth_verifier']),
    );
    unset($_SESSION['token']);
    unset($_SESSION['token_secret']);
    $user_id = $atoken['user_id'];
    $screen_name = $atoken['screen_name'];
    $access_token     = $atoken['oauth_token'];
    $access_token_secret = $atoken['oauth_token_secret'];
    if ($screen_name != '') {
        $_SESSION['user_id'] = $user_id;
        $_SESSION['screen_name'] = $screen_name;
        $rs = pg_execute(
            $pgconn,
            "UPDATEAUTH",
            array(
                $access_token, $access_token_secret,
                strtolower($screen_name), $user_id
            )
        );
        if (pg_num_rows($rs) == 0) {
            pg_execute(
                $pgconn,
                "SAVEAUTH",
                array(
                    $user_id, strtolower($screen_name),
                    $access_token, $access_token_secret
                )
            );
        }
        reloadbot();
    }
    $msg[] = sprintf("Saved authorization for user %s", $screen_name);
}
if ($screen_name == '') {
    $connection = new TwitterOAuth(TWITTER_KEY, TWITTER_SECRET);
    $request_token = $connection->oauth(
        "oauth/request_token",
        ["oauth_callback" => "https://mesonet.agron.iastate.edu/projects/iembot/twitter.php?cb"]
    );
    $_SESSION['token'] = $token = $request_token['oauth_token'];
    $_SESSION['token_secret'] = $request_token['oauth_token_secret'];
    $authUrl = $connection->url("oauth/authorize", array("oauth_token" => $token));
    header("Location: $authUrl");
    exit;
}

$sselect2 = "";
$rs = pg_execute($pgconn, "SELECTSUBS", array($user_id));
for ($i = 0; $row = pg_fetch_array($rs); $i++) {
    $sselect2 .= sprintf(
        '<tr><th>%s</th><td>%s</td>
        <td><a href="?del&amp;channel=%s">Unsubscribe</a></tr>',
        $screen_name,
        $row['channel'],
        $row['channel']
    );
}

$msghtml = "";
foreach ($msg as $key => $val) {
    $msghtml .= "<div class='alert alert-info'>{$val}</div>";
}

$t = new MyView();
$t->title = "IEMBot Twitter Configuration Page";

$t->content = <<<EOM

<ol class="breadcrumb">
 <li><a href="/projects/iembot/">IEMBot Homepage</a></li>
 <li class="active">Twitter Configuration Page</li>
</ol>

{$msghtml}

<h3>IEMBOT + Twitter Integration</h3>

<p>This page allows for the subscription of a Twitter Account to one or more
"<a href="/projects/iembot/#channels" target="_blank">IEMBot channels</a>".
The automated processing of National Weather Service text
products converts each product into a tweet sized message and is associated
with one or more channels.  These channels are then used to route the messages
to subscribed twitter pages.  A deduplication process should prevent a single
message from posting twice to your account.</p>

<div class="alert alert-warning">This service is provided as-is and without
warranty.  <strong>The service could fail</strong> with an EF-5 tornado approaching your
city, so you have been warned!</div>

<div class="well">
<h4>Add Channel Subscription</h4>
 <form method="POST" action="twitter.php">
 <input type="hidden" name="add" value="yes"/>
 <table class="table">
 <tr><td>Page</td><td>Channel</td></tr>
 <tr><th>{$screen_name}</th>
  <td><input type="text" name="channel" /></tr>
 </table>
 <input type="submit" name="Subscribe Channel" />
 </form>
</div>

<div class="well">
<h4>Current Subscriptions</h4>
 <table class="table table-striped">
 <thead><tr><th>Page</th><th>Channel</th><th></th></tr></thead>
{$sselect2}
 </table>
</div> 		

<div class="well">
<h4>Delete IEMBot from my account</h4>

<p><strong>WARNING:</strong> This will delete all of your IEMBot subscriptions
and remove your OpenAuth tokens from the IEMBot database. This should prevent
any future posts to your page on IEMbot's behalf.</p>

<p><button class="btn btn-danger" onclick="if (confirm('Are you sure?')){
    window.location.href='/projects/iembot/twitter.php?removeme=1';}">Delete IEMBot</button></p>
</div>

EOM;

$t->render('single.phtml');
