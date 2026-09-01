import json

import BigWorld  # type: ignore
import urllib2  # type: ignore
from ap_calculator.debug import VERSION
from PlayerEvents import g_playerEvents  # type: ignore

has_logged = False
URL = "https://wot-telemetry.onrender.com/"


def send(payload):
    try:
        data = json.dumps(payload)
        req = urllib2.Request(
            URL,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        urllib2.urlopen(req, timeout=5).read()
    except:
        print("Ran into exception when trying to send payload.")


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
            has_logged = True
        except:
            print("Ran into exception when trying to get payload information.")


def init():
    g_playerEvents.onAccountShowGUI += _on_account_show_gui


init()
