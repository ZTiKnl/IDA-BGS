import sys
import json
import requests
import threading
import Tkinter as tk
import myNotebook as nb
from config import config

this = sys.modules[__name__]

def plugin_start(plugin_dir):
   """
   Load this plugin into EDMC
   """
   print "IDA-BGS loaded! My plugin folder is {}".format(plugin_dir.encode("utf-8"))
   return "IDA-BGS"

def plugin_stop():
    """
    EDMC is closing
    """
    print "Closing down"

def plugin_prefs(parent, cmdr, is_beta):
   """
   Return a TK Frame for adding to the EDMC settings dialog.
   """
   this.apikey = tk.StringVar(value=config.get("APIkey"))

   frame = nb.Frame(parent)

   plugin_label = nb.Label(frame, text="IDA-BGS EDMC plugin v0.11")
   plugin_label.grid(padx=10, row=0, column=0, sticky=tk.W)

   empty_label = nb.Label(frame, text="")
   empty_label.grid(padx=10, row=1, column=0, sticky=tk.W)

   apikey_label = nb.Label(frame, text="Enter your API key to authorize data transfers")
   apikey_label.grid(padx=10, row=2, column=0, sticky=tk.W)

   apikey_entry = nb.Entry(frame, textvariable=this.apikey)
   apikey_entry.grid(padx=10, row=2, column=1, columnspan=2, sticky=tk.EW)

   empty_label = nb.Label(frame, text="")
   empty_label.grid(padx=10, row=3, column=0, sticky=tk.W)

   secure_label = nb.Label(frame, text="All data is sent over a secure connection (SSL)")
   secure_label.grid(padx=10, row=4, column=0, sticky=tk.W)

   empty_label = nb.Label(frame, text="")
   empty_label.grid(padx=10, row=5, column=0, sticky=tk.W)

   data_label = nb.Label(frame, text="The only data sent is BGS faction data along with basic system details and a timestamp upon jumping into a system")
   data_label.grid(padx=10, row=6, column=0, sticky=tk.W)

   data_label = nb.Label(frame, text="It also sends data about systems where IDA does NOT have a presence, but this data is ignored by the API")
   data_label.grid(padx=10, row=7, column=0, sticky=tk.W)

   data_label = nb.Label(frame, text="Each data package is between 100KB - 500KB, only 1 data package is sent per FSD jump")
   data_label.grid(padx=10, row=8, column=0, sticky=tk.W)

   empty_label = nb.Label(frame, text="")
   empty_label.grid(padx=10, row=9, column=0, sticky=tk.W)

   thirdparty_label = nb.Label(frame, text="No data will be sold to third parties, and there are no tracking mechanisms trying to follow you")
   thirdparty_label.grid(padx=10, row=10, column=0, sticky=tk.W)

   return frame

def prefs_changed(cmdr, is_beta):
   """
   Save settings.
   """
   config.set('APIkey', this.apikey.get())

def plugin_app(parent):
    """
    Create a pair of TK widgets for the EDMC main window
    """
    label = tk.Label(parent, text="IDA BGS:")

    this.status = tk.Label(parent, text="Idle", foreground="SystemButtonText")

    orig_color = label.cget("highlightcolor")
    sys.stderr.write("color: " + str(orig_color) + "\n")

    return (label, this.status)

def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    Evaluate data and transfer to https://ida-bgs.ztik.nl/api.php
    """
    if entry['event'] == 'FSDJump':
        # We arrived at a new system!
	sys.stderr.write("Arrived at {}, sending data to server\n".format(entry['StarSystem']))
        this.apikey = tk.StringVar(value=config.get("APIkey"))

        entry['key'] = this.apikey.get()

        this.status['text'] = "Sending data..."
        url = "https://ida-bgs.ztik.nl/api.php"
        r = requests.post(url, json=entry)
        if r.status_code == 200:
            sys.stderr.write("Status: 200\n")
            this.status['text'] = "Success: data sent"
            t = threading.Timer(10.0, clearstatus)
        else:
            if r.status_code == 201:
                sys.stderr.write("Status: 201\n")
                this.status['text'] = "Success: no data sent"
                t = threading.Timer(10.0, clearstatus)
            else:
                data = json.loads(r.text)
                sys.stderr.write("Status: " + str(r.status_code) + ": " + str(data['message']) + "\n")
                sys.stderr.write("Error: " + str(data['error']) + "\n")
                this.status['text'] = "Fail: " + str(r.status_code) + ": " + str(data['message'])
                this.status['foreground'] = "red"
                t = threading.Timer(30.0, clearstatus)
        t.start()

def clearstatus():
    this.status['text'] = "SystemButtonText"