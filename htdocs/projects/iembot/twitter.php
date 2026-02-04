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
if (TWITTER_KEY == null || TWITTER_SECRET == null) {
    http_response_code(422);
    die("Twitter API keys not configured, please contact the IEM.");
}


$user_id = isset($_SESSION["user_id"]) ? $_SESSION["user_id"] : null;
$screen_name = isset($_SESSION["screen_name"]) ? $_SESSION["screen_name"] : null;
$iembot_account_id = isset($_SESSION["iembot_account_id"]) ? $_SESSION["iembot_account_id"] : null;

$channel = strtoupper(get_str404("channel", ''));
$channel = trim($channel);

$pgconn = iemdb('iembot');

$st_saveauth = iem_pg_prepare($pgconn, "INSERT into " .
    "iembot_twitter_oauth " .
    "(user_id, screen_name, access_token, access_token_secret, iembot_account_id) " .
    "VALUES ($1,$2,$3,$4,(select create_iembot_account($5))) ".
    "returning iembot_account_id");
$st_updateauth = iem_pg_prepare($pgconn, "UPDATE iembot_twitter_oauth " .
    "SET access_token = $1, access_token_secret = $2, updated = now(), " .
    "screen_name = $3 WHERE user_id = $4 RETURNING screen_name, iembot_account_id");
$st_deleteauth = iem_pg_prepare(
    $pgconn,
    "DELETE from iembot_twitter_oauth where user_id = $1",
);
$st_selectsubs = iem_pg_prepare($pgconn, <<<EOM
    select channel_name from iembot_channels c, iembot_subscriptions s
    where s.iembot_account_id = $1 and c.id = s.channel_id
    ORDER by channel_name ASC
EOM
);
$st_addsub = iem_pg_prepare($pgconn, <<<EOM
    insert into iembot_subscriptions(iembot_account_id, channel_id)
    values ($1, (select get_or_create_iembot_channel_id($2)))
EOM
);
$st_delsub = iem_pg_prepare($pgconn, <<<EOM
    delete from iembot_subscriptions s using iembot_channels c
    where s.channel_id = c.id and s.iembot_account_id = $1
    and c.channel_name = $2
EOM
);
$st_deletesubs = iem_pg_prepare(
    $pgconn,
    "DELETE from iembot_subscriptions where iembot_account_id = $1",
);


function reloadbot()
{
    return file_get_contents("http://iembot:9003/reload");
}

$msg = array();
//------------------------------------------------------------
if (array_key_exists("removeme", $_REQUEST) && $_REQUEST["removeme"] == "1") {
    // remove subs first due to foreign key constraints
    pg_execute($pgconn, $st_deletesubs, array($iembot_account_id));
    pg_execute($pgconn, $st_deleteauth, array($user_id));
    $msg[] = "You have been removed from the bot.";
    reloadbot();
    unset($_SESSION["user_id"]);
    unset($_SESSION["screen_name"]);
}
if (array_key_exists('add', $_REQUEST) && $channel != '' && $screen_name != '') {
    pg_execute($pgconn, $st_addsub, array(
        $iembot_account_id,
        $channel
    ));
    reloadbot();
    $msg[] = sprintf(
        "Added channel subscription %s for user %s, reloaded bot",
        $channel,
        $_SESSION["screen_name"]
    );
}
if (array_key_exists('del', $_REQUEST) && $channel != '' && $screen_name != '') {
    pg_execute($pgconn, $st_delsub, array(
        $iembot_account_id,
        $channel
    ));
    reloadbot();
    $msg[] = sprintf(
        "Deleted channel subscription %s for user %s, reloaded bot",
        $channel,
        $_SESSION["screen_name"]
    );
}
if (array_key_exists('cb', $_REQUEST) && isset($_SESSION['token']) && isset($_SESSION['token_secret'])) {
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
            $st_updateauth,
            array(
                $access_token,
                $access_token_secret,
                strtolower($screen_name),
                $user_id
            )
        );
        if (pg_num_rows($rs) == 0) {
            $rs = pg_execute(
                $pgconn,
                $st_saveauth,
                array(
                    $user_id,
                    strtolower($screen_name),
                    $access_token,
                    $access_token_secret,
                    "twitter",
                )
            );
        }
        $row = pg_fetch_assoc($rs);
        $_SESSION['iembot_account_id'] = $row['iembot_account_id'];
        $iembot_account_id = $row['iembot_account_id'];
        reloadbot();
    }
    $msg[] = sprintf("Saved authorization for user %s", $screen_name);
}
// Careful this is done after the oauth flow above
if (is_null($screen_name) || is_null($iembot_account_id)) {
    $connection = new TwitterOAuth(TWITTER_KEY, TWITTER_SECRET);
    $request_token = $connection->oauth(
        "oauth/request_token",
        ["oauth_callback" => "{$EXTERNAL_BASEURL}/projects/iembot/twitter.php?cb"]
    );
    $_SESSION['token'] = $token = $request_token['oauth_token'];
    $_SESSION['token_secret'] = $request_token['oauth_token_secret'];
    $authUrl = $connection->url("oauth/authorize", array("oauth_token" => $token));
    header("Location: $authUrl");
    exit;
}

$sselect2 = "";
$rs = pg_execute($pgconn, $st_selectsubs, array($iembot_account_id));
while ($row = pg_fetch_assoc($rs)) {
    $sselect2 .= sprintf(
        '<tr><th>%s</th><td>%s</td>
        <td><a href="?del&amp;channel=%s">Unsubscribe</a></tr>',
        $screen_name,
        $row['channel_name'],
        $row['channel_name']
    );
}

$msghtml = "";
foreach ($msg as $key => $val) {
    $msghtml .= "<div class='alert alert-info'>{$val}</div>";
}

$t = new MyView();
$t->title = "IEMBot Twitter Configuration Page";


$t->content = <<<EOM

<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/projects/iembot/">IEMBot Homepage</a></li>
        <li class="breadcrumb-item active" aria-current="page">Twitter Configuration Page</li>
    </ol>
</nav>

{$msghtml}

<h3 class="mt-4 mb-3">IEMBOT + Twitter Integration</h3>

<p>This page allows for the subscription of a Twitter Account to one or more
<a href="/projects/iembot/#channels" target="_blank">IEMBot channels</a>.
The automated processing of National Weather Service text products converts each product into a tweet-sized message and is associated
with one or more channels. These channels are then used to route the messages to subscribed Twitter pages. A deduplication process should prevent a single message from posting twice to your account.</p>

<div class="alert alert-warning" role="alert">
    This service is provided as-is and without warranty. <strong>The service could fail</strong> with an EF-5 tornado approaching your city, so you have been warned!
</div>

<div class="card my-4">
    <div class="card-body">
        <h4 class="card-title">Add Channel Subscription</h4>
        <form method="POST" action="twitter.php">
            <input type="hidden" name="add" value="yes" />
            <div class="mb-3">
                <label for="page" class="form-label">Page</label>
                <input type="text" class="form-control-plaintext" id="page" readonly value="{$screen_name}" />
            </div>
            <div class="mb-3">
                <label for="channel" class="form-label">Channel</label>
                <input type="text" class="form-control" name="channel" id="channel" required />
            </div>
            <button type="submit" class="btn btn-primary">Subscribe Channel</button>
        </form>
    </div>
</div>

<div class="card my-4">
    <div class="card-body">
        <h4 class="card-title">Current Subscriptions</h4>
        <div class="table-responsive">
            <table class="table table-striped align-middle">
                <thead>
                    <tr><th>Page</th><th>Channel</th><th></th></tr>
                </thead>
                <tbody>
                    {$sselect2}
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="card my-4">
    <div class="card-body">
        <h4 class="card-title">Delete IEMBot from my account</h4>
        <p><strong>WARNING:</strong> This will delete all of your IEMBot subscriptions and remove your OpenAuth tokens from the IEMBot database. This should prevent any future posts to your page on IEMbot's behalf.</p>
        <button class="btn btn-danger" type="button" onclick="if (confirm('Are you sure?')){window.location.href='/projects/iembot/twitter.php?removeme=1';}">Delete IEMBot</button>
    </div>
</div>

EOM;

$t->render('single.phtml');
