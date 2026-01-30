"""
IEM Slack Bot OAuth and Subscription Handlers
"""

import json
import urllib.parse

import httpx
from pyiem.database import sql_helper, with_sqlalchemy_conn
from pyiem.util import get_properties
from pyiem.webutil import iemapp
from sqlalchemy.engine import Connection

# These should be set in your environment or config
SLACK_CLIENT_ID = get_properties().get("bot.slack.client_id", "changeme")
SLACK_CLIENT_SECRET = get_properties().get(
    "bot.slack.client_secret", "changeme"
)
SLACK_REDIRECT_URI = get_properties().get(
    "bot.slack.redirect_uri",
    "https://iem.local/projects/iembot/slack/oauth/callback",
)


def slack_install(_environ: dict, start_response: callable):
    """Redirect user to Slack OAuth install page."""
    params = {
        "client_id": SLACK_CLIENT_ID,
        "scope": (
            "chat:write,channels:read,groups:read,im:read,mpim:read,commands",
        ),
        "user_scope": "",
        "redirect_uri": SLACK_REDIRECT_URI,
    }
    url = "https://slack.com/oauth/v2/authorize?" + urllib.parse.urlencode(
        params
    )
    start_response("302 Found", [("Location", url)])
    return [b""]


@with_sqlalchemy_conn("mesosite")
def slack_oauth_callback(
    environ: dict, start_response: callable, conn: Connection | None = None
):
    """Handle Slack OAuth callback, exchange code for tokens."""
    # Parse query string
    query = environ.get("QUERY_STRING", "")
    params = urllib.parse.parse_qs(query)
    code = params.get("code", [None])[0]
    if not code:
        start_response("400 Bad Request", [("Content-Type", "text/plain")])
        return [b"Missing code parameter"]
    # Exchange code for token
    token_url = "https://slack.com/api/oauth.v2.access"
    data = {
        "client_id": SLACK_CLIENT_ID,
        "client_secret": SLACK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": SLACK_REDIRECT_URI,
    }
    resp = httpx.post(token_url, data=data)
    resp_json = resp.json()
    if not resp_json.get("ok"):
        start_response("400 Bad Request", [("Content-Type", "text/plain")])
        return [
            f"Slack OAuth failed: {resp_json.get('error', 'unknown')}".encode()
        ]
    # Save tokens and team info to DB here (implement as needed)
    conn.execute(
        sql_helper("""
    insert into iembot_slack_teams
        (team_id, team_name, access_token, bot_user_id)
    values (:team_id, :team_name, :access_token, :bot_user_id)
    on conflict (team_id) do update set
    access_token = excluded.access_token,
    bot_user_id = excluded.bot_user_id,
    team_name = excluded.team_name
    """),
        {
            "team_id": resp_json["team"]["id"],
            "team_name": resp_json["team"]["name"],
            "access_token": resp_json["access_token"],
            "bot_user_id": resp_json["bot_user_id"],
        },
    )
    conn.commit()

    start_response("200 OK", [("Content-Type", "text/html")])
    return [
        b"<h1>Slack app installed!</h1><p>You may now close this window.</p>"
    ]


@with_sqlalchemy_conn("mesosite")
def slack_subscribe(
    environ: dict, start_response: callable, conn: Connection | None = None
):
    """Subscribe a channel to a subkey (product key)."""
    # Expect POST with form: team_id, channel_id, subkey
    try:
        size = int(environ.get("CONTENT_LENGTH", 0))
        body = environ["wsgi.input"].read(size).decode()
        params = urllib.parse.parse_qs(body)
    except Exception:
        params = {}
    # Slack slash command: team_id, channel_id, text (subkey)
    team_id = params.get("team_id", [None])[0]
    channel_id = params.get("channel_id", [None])[0]
    subkey = params.get("text", [None])[0]
    if not (team_id and channel_id and subkey):
        start_response("200 OK", [("Content-Type", "application/json")])
        return [
            b'{"response_type":"ephemeral","text":"Missing team_id, '
            b'channel_id, or subkey (usage: /iembot_subscribe [product_key])"}'
        ]
    try:
        conn.execute(
            sql_helper("""
            insert into iembot_slack_subscriptions(team_id, channel_id, subkey)
            values (:team_id, :channel_id, :subkey)
            on conflict do nothing
            """),
            {"team_id": team_id, "channel_id": channel_id, "subkey": subkey},
        )
        conn.commit()
        start_response("200 OK", [("Content-Type", "application/json")])
        resp = {
            "response_type": "ephemeral",
            "text": f"Channel <#{channel_id}> is now subscribed to {subkey}.",
        }
        return [json.dumps(resp).encode()]
    except Exception as e:
        start_response("200 OK", [("Content-Type", "application/json")])
        resp = {
            "response_type": "ephemeral",
            "text": f"Subscription failed: {e}",
        }
        return [json.dumps(resp).encode()]


@with_sqlalchemy_conn("mesosite")
def slack_unsubscribe(
    environ: dict, start_response: callable, conn: Connection | None = None
):
    """Unsubscribe a channel from a subkey (product key)."""
    # Expect POST with form: team_id, channel_id, subkey
    try:
        size = int(environ.get("CONTENT_LENGTH", 0))
        body = environ["wsgi.input"].read(size).decode()
        params = urllib.parse.parse_qs(body)
    except Exception:
        params = {}
    # Slack slash command: team_id, channel_id, text (subkey)
    team_id = params.get("team_id", [None])[0]
    channel_id = params.get("channel_id", [None])[0]
    subkey = params.get("text", [None])[0]
    if not (team_id and channel_id and subkey):
        start_response("200 OK", [("Content-Type", "application/json")])
        return [
            b'{"response_type":"ephemeral","text":"Missing team_id, '
            b"channel_id, or subkey (usage: /iembot_unsubscribe "
            b'[product_key])"}'
        ]
    try:
        conn.execute(
            sql_helper("""
            delete from iembot_slack_subscriptions
            where team_id = :team_id and channel_id = :channel_id
            and subkey = :subkey
            """),
            {"team_id": team_id, "channel_id": channel_id, "subkey": subkey},
        )
        conn.commit()
        start_response("200 OK", [("Content-Type", "application/json")])
        resp = {
            "response_type": "ephemeral",
            "text": (
                f"Channel <#{channel_id}> is now unsubscribed from {subkey}."
            ),
        }
        return [json.dumps(resp).encode()]
    except Exception as e:
        start_response("200 OK", [("Content-Type", "application/json")])
        resp = {
            "response_type": "ephemeral",
            "text": f"Unsubscribe failed: {e}",
        }
        return [json.dumps(resp).encode()]


@iemapp()
def application(environ: dict, start_response: callable):
    """Our entry point."""
    path = environ.get("PATH_INFO", "")
    if path == "/install":
        return slack_install(environ, start_response)
    elif path == "/oauth/callback":
        return slack_oauth_callback(environ, start_response)

    # Subscription endpoints
    if path == "/subscribe":
        return slack_subscribe(environ, start_response)
    elif path == "/unsubscribe":
        return slack_unsubscribe(environ, start_response)

    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"IEM Slack Bot Endpoint"]
