import urllib2  # type: ignore
import json
import BigWorld  # type: ignore
from PlayerEvents import g_playerEvents  # type: ignore
from APCalculator.debug import VERSION

has_logged = False
URL = "https://wot-telemetry.onrender.com/"


def get_name():
    try:
        return BigWorld.player().name
    except:
        return "Name Error"


def send(payload):
    try:
        data = json.dumps(payload)
        req = urllib2.Request(
            URL,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        urllib2.urlopen(req, timeout=5).read()
    except Exception:
        pass


def _on_account_show_gui(ctx):
    global has_logged
    if not has_logged:
        try:
            p = BigWorld.player()
            send(
                {
                    "username": p.name,
                    "server": p.connectionMgr.serverUserName,
                    "mod_version": VERSION,
                }
            )
        except:
            pass
        has_logged = True


def init():
    g_playerEvents.onAccountShowGUI += _on_account_show_gui


init()
