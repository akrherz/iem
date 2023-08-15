"""
Configure iembot for mastodon, gasp.
"""

import mastodon
import requests
from cryptography.fernet import Fernet
from paste.request import get_cookie_dict, parse_formvars
from pyiem.templates.iem import TEMPLATE
from pyiem.util import get_dbconn, get_properties

PRIVKEY = (get_properties()["mod_wsgi.privkey"]).encode("ascii")
APP = "https://mesonet.agron.iastate.edu/projects/iembot/mastodon"
HEADER = """
<ol class="breadcrumb">
 <li><a href="/projects/iembot/">IEMBot Homepage</a></li>
 <li class="active">Mastodon Subscription</li>
</ol>

<h3>Highly Experimental IEMBot to Mastodon Configuration:</h3>

<p>There are absolutely no warranties with this service.  Use at your own
risk and peril!</p>

"""
ENTER_HOST_FORM = """
<h3>Enter your Mastodon instance address</h3>
<form method="GET" action="/projects/iembot/mastodon/" name="s">
https://<input type="text" name="s" size="60">
<input type="submit">
</form>
"""
TEST_MESSAGE = "Hello, this is a test message from the IEMBot integration."


def get_mastodon_app(server):
    """Get or create an app."""
    redirect_uri = f"{APP}/?s={server}"
    conn = get_dbconn("mesosite")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT client_id, client_secret from iembot_mastodon_apps WHERE
        server = %s
        """,
        (server,),
    )
    if cursor.rowcount == 1:
        (client_id, client_secret) = cursor.fetchone()
    else:
        api = mastodon.Mastodon(api_base_url=f"https://{server}")
        (client_id, client_secret) = api.create_app(
            "iembot",
            api_base_url=f"https://{server}",
            redirect_uris=[redirect_uri],
        )
        cursor.execute(
            """
            insert into iembot_mastodon_apps(server, client_id, client_secret)
            values(%s, %s, %s)
            """,
            (server, client_id, client_secret),
        )
        cursor.close()
        conn.commit()
    mapp = mastodon.Mastodon(
        client_id=client_id,
        client_secret=client_secret,
        api_base_url=f"https://{server}",
    )
    return mapp, mapp.auth_request_url(redirect_uris=redirect_uri)


def get_app4user(cookies):
    """Do we know who we have here?"""
    mm = cookies.get("mm")
    if mm is None or mm == "":
        return None
    # Decrpyt this
    try:
        user_id = int(Fernet(PRIVKEY).decrypt(mm.encode("ascii")))
    except Exception:
        return None
    conn = get_dbconn("mesosite")
    cursor = conn.cursor()
    cursor.execute(
        """
        select access_token, server from iembot_mastodon_oauth o,
        iembot_mastodon_apps a where o.id = %s and o.appid = a.id
        and access_token is not null
        """,
        (user_id,),
    )
    if cursor.rowcount != 1:
        return None
    row = cursor.fetchone()
    mapp = mastodon.Mastodon(
        access_token=row[0],
        api_base_url=f"https://{row[1]}",
    )
    try:
        mapp.me()
    except Exception as exp:
        print(f"Removing access_token for {user_id} due to {exp}")
        cursor.execute(
            """
            update iembot_mastodon_oauth SET access_token = null,
            updated = now() where id = %s
            """,
            (user_id,),
        )
        cursor.close()
        conn.commit()
        return None
    # For better or likely worse, we tag along this attribute
    mapp.iembot_user_id = user_id
    return mapp


def build_subui(mapp, fdict):
    """Show the subscriptions."""
    conn = get_dbconn("mesosite")
    cursor = conn.cursor()
    log = []
    if fdict.get("testmsg") is not None:
        try:
            res = mapp.status_post(status=TEST_MESSAGE)
            log.append(
                f"Test post to Mastodon is <a href=\"{res['uri']}\">here</a>"
            )
        except Exception as exp:
            log.append(f"Posting test message resulted in error: {exp}")
    channel = fdict.get("add")
    if channel is not None and channel != "":
        cursor.execute(
            """
            insert into iembot_mastodon_subs(user_id, channel)
            values (%s, %s)
            """,
            (mapp.iembot_user_id, channel.upper()),
        )
        log.append(f"Added channel subscription for |{channel.upper()}")
        reload_bot()
    channel = fdict.get("del")
    if channel is not None and channel != "":
        cursor.execute(
            """
            delete from iembot_mastodon_subs where user_id = %s
            and channel = %s
            """,
            (mapp.iembot_user_id, channel.upper()),
        )
        log.append(f"Deleted channel subscription for |{channel.upper()}")
        reload_bot()
    cursor.execute(
        """
        SELECT channel from iembot_mastodon_subs WHERE user_id = %s
        ORDER by channel asc
        """,
        (mapp.iembot_user_id,),
    )
    logmsg = "" if not log else f"<h3>Log Messages</h3> {'<br/>'.join(log)}"
    res = f"""
{logmsg}

<p><a href="/projects/iembot/mastodon/?testmsg"
 class="btn btn-default">Post Test Message</a>

<form method="GET" name="sub">
<input type="text" name="add" size="10">
<input type="submit" value="Add Channel">
</form>

    <h3>Currently Subscribed Channels.</h3>
    """
    for row in cursor:
        du = f"/projects/iembot/mastodon/?del={row[0]}"
        res += f'<p><strong>{row[0]}</strong> <a href="{du}">Delete</a></p>'

    return res


def sanitize_server(val):
    """Ensure we have something that is like a server."""
    if val is None:
        return None
    if val.startswith("https://"):
        return val[8:]
    return val.split("@")[-1].rstrip("/")


def save_code(mapp, server, code, headers):
    """Persist to database."""
    # Exchange the code for an access token
    redirect_uri = f"{APP}/?s={server}"
    access_token = mapp.log_in(
        code=code,
        redirect_uri=redirect_uri,
    )
    mapp = mastodon.Mastodon(
        api_base_url=f"https://{server}",
        access_token=access_token,
    )
    me = mapp.me()
    conn = get_dbconn("mesosite")
    cursor = conn.cursor()
    # Ensure we have no current entry
    cursor.execute(
        """
        select id from iembot_mastodon_oauth where screen_name = %s
        and appid = (select id from iembot_mastodon_apps where server = %s)
        """,
        (me["username"], server),
    )
    if cursor.rowcount == 0:
        cursor.execute(
            """
            insert into iembot_mastodon_oauth(appid, screen_name)
            values
            (
                (select id from iembot_mastodon_apps where server = %s),
                %s
            ) returning id
            """,
            (server, me["username"]),
        )
    mapp.iembot_user_id = cursor.fetchone()[0]
    cursor.execute(
        """
        update iembot_mastodon_oauth SET access_token = %s,
        updated = now() WHERE id = %s
        """,
        (access_token, mapp.iembot_user_id),
    )
    cursor.close()
    conn.commit()
    # Set a cookie
    text = (
        Fernet(PRIVKEY)
        .encrypt(str(mapp.iembot_user_id).encode("ascii"))
        .decode("ascii")
    )
    headers.append(
        (
            "Set-Cookie",
            f"mm={text}; Path=/projects/iembot/mastodon/; Max-Age=8640000",
        )
    )
    return mapp


def reload_bot():
    """Tell iembot to refresh."""
    requests.get("http://iembot:9003/reload", timeout=5)


def application(environ, start_response):
    """mod-wsgi handler."""
    fdict = parse_formvars(environ)
    cookies = get_cookie_dict(environ)
    headers = [("Content-type", "text/html")]
    res = {"content": HEADER}

    # Inspect cookies to see if we have details on our Mastodon user here
    mapp = get_app4user(cookies)
    # If we have an app, we can show the subscriptions and be done.
    if mapp is not None:
        start_response("200 OK", headers)
        res["content"] += build_subui(mapp, fdict)
        return [TEMPLATE.render(res).encode("utf-8")]

    # We should now have a server set, if not, we need to prompt for one.
    server = sanitize_server(fdict.get("s"))
    if server is None:
        start_response("200 OK", headers)
        res["content"] += ENTER_HOST_FORM
        return [TEMPLATE.render(res).encode("utf-8")]
    # Get the app
    mapp, redirect_uri = get_mastodon_app(server)
    # oauth step
    if fdict.get("code") is None:
        headers = [("Location", redirect_uri)]
        start_response("307 Temporary redirect", headers)
        return [TEMPLATE.render(res).encode("utf-8")]
    # Also sets cookie
    mapp = save_code(mapp, server, fdict.get("code"), headers)
    res["content"] += build_subui(mapp, fdict)
    start_response("200 OK", headers)
    return [TEMPLATE.render(res).encode("utf-8")]
