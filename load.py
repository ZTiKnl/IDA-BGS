import sys
import json
import requests
import threading
try:
    import Tkinter as tk # this is for python2
except:
    import tkinter as tk # this is for python3
from ttkHyperlinkLabel import HyperlinkLabel
import myNotebook as nb
from config import config

this = sys.modules[__name__]

def plugin_start3(plugin_dir):
    return plugin_start(plugin_dir)

def plugin_start(plugin_dir):
    """
    Load this plugin into EDMC
    """
    print("IDA-BGS loaded! My plugin folder is " + format(plugin_dir))
    return "IDA-BGS"

def plugin_stop():
    """
    EDMC is closing
    """
    print("Closing down")

def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    this.apikey = tk.StringVar(value=config.get("APIkey"))
    this.approvedatatransfer = tk.IntVar(value=config.getint("ADT"))

    frame = nb.Frame(parent)

    plugin_label = nb.Label(frame, text="IDA-BGS EDMC plugin v0.65")
    plugin_label.grid(padx=10, row=0, column=0, sticky=tk.W)

    HyperlinkLabel(frame, text='Visit website', background=nb.Label().cget('background'), url='https://github.com/ZTiKnl/IDA-BGS', underline=True).grid(padx=10, row=0, column=1, sticky=tk.W)

    empty_label = nb.Label(frame, text="")
    empty_label.grid(padx=10, row=1, column=0, columnspan=2, sticky=tk.W)

    apikey_label = nb.Label(frame, text="Enter your API key to authorize data transfers")
    apikey_label.grid(padx=10, row=2, column=0, sticky=tk.W)

    apikey_entry = nb.Entry(frame, textvariable=this.apikey)
    apikey_entry.grid(padx=10, row=2, column=1, sticky=tk.EW)

    data_label = nb.Label(frame, text="Each data package is between 1KB - 5KB, only 1 data package is sent per FSD jump")
    data_label.grid(padx=20, row=3, column=0, columnspan=2, sticky=tk.W)

    data_label = nb.Label(frame, text="The only data sent is BGS faction data along with basic system details and a timestamp")
    data_label.grid(padx=20, row=4, column=0, columnspan=2, sticky=tk.W)

    data_label = nb.Label(frame, text="It also sends data about systems where IDA does NOT have a presence, but this data is ignored by the API")
    data_label.grid(padx=20, row=5, column=0, columnspan=2, sticky=tk.W)

    empty_label = nb.Label(frame, text="")
    empty_label.grid(padx=10, row=6, column=0, columnspan=2, sticky=tk.W)

    optin_entry = nb.Checkbutton(frame, text=_('Send additional data'), variable=this.approvedatatransfer)
    optin_entry.grid(padx=10, row=7, column=0, columnspan=2, sticky=tk.EW)

    data_label = nb.Label(frame, text="Each data package is between 2KB - 10KB, 1 data package is sent per event")
    data_label.grid(padx=20, row=8, column=0, columnspan=2, sticky=tk.W)

    events_label = nb.Label(frame, text="Events that are processed:")
    events_label.grid(padx=20, row=9, column=0, columnspan=2, sticky=tk.W)

    events_label = nb.Label(frame, text="Mission Completed")
    events_label.grid(padx=30, row=10, column=0, columnspan=2, sticky=tk.W)

    events_label = nb.Label(frame, text="Sell Exploration Data")
    events_label.grid(padx=30, row=11, column=0, columnspan=2, sticky=tk.W)

    events_label = nb.Label(frame, text="Cash in Bounty Voucher")
    events_label.grid(padx=30, row=12, column=0, columnspan=2, sticky=tk.W)

    events_label = nb.Label(frame, text="Sell Cargo on Market")
    events_label.grid(padx=30, row=13, column=0, columnspan=2, sticky=tk.W)

    empty_label = nb.Label(frame, text="")
    empty_label.grid(padx=10, row=14, column=0, columnspan=2, sticky=tk.W)

    thirdparty_label = nb.Label(frame, text="No data will be sold to third parties, and there are no tracking mechanisms trying to follow you")
    thirdparty_label.grid(padx=10, row=15, column=0, columnspan=2, sticky=tk.W)

    return frame

def prefs_changed(cmdr, is_beta):
    """
    Save settings.
    """
    config.set('APIkey', this.apikey.get())
    config.set('ADT', this.approvedatatransfer.get())

def plugin_app(parent):
    """
    Create a pair of TK widgets for the EDMC main window
    """
    label = tk.Label(parent, text="IDA BGS:")
    this.status = tk.Label(parent, text="Idle", anchor="w")

    return (label, this.status)

def journal_entry(cmdr, is_beta, system, station, entry, state):
    """
    Evaluate data and transfer to https://ida-bgs.ztik.nl/api/input
    """
    if entry['event'] == 'FSDJump':
        # We arrived at a new system!
        sys.stderr.write("Arrived at {}, sending data to server\n".format(entry['StarSystem']))
        this.apikey = tk.StringVar(value=config.get("APIkey"))

        entry['key'] = this.apikey.get()

        entry['JumpDist'] = ''
        entry['FuelLevel'] = ''
        entry['BodyID'] = ''
        entry['Body'] = ''
        entry['BodyType'] = ''
        entry['FuelUsed'] = ''

        this.status['text'] = "Sending BGS data..."
        url = "https://ida-bgs.ztik.nl/api/input"
        r = requests.post(url, json=entry)
        if r.status_code == 200:
            sys.stderr.write("Status: 200\n")
            this.status['text'] = "Success: BGS data sent"
            t = threading.Timer(5.0, clearstatus)
        else:
            if r.status_code == 201:
                sys.stderr.write("Status: 201\n")
                this.status['text'] = "Success: BGS data n/a"
                t = threading.Timer(5.0, clearstatus)
            else:
                if r.status_code == 202:
                    sys.stderr.write("Status: 202\n")
                    this.status['text'] = "Success: API not ready"
                    t = threading.Timer(5.0, clearstatus)
                else:
                    data = json.loads(r.text)
                    sys.stderr.write("Status BGS: " + str(r.status_code) + ": " + str(data['message']) + "\n")
                    sys.stderr.write("Error BGS: " + str(data['error']) + "\n")
                    this.status['text'] = "Fail: " + str(r.status_code) + ": " + str(data['message'])
                    t = threading.Timer(10.0, clearstatus)
        t.start()

    if entry['event'] == 'Docked':
        # We arrived at a new system!
        sys.stderr.write("Arrived at {}, sending data to server\n".format(entry['StarSystem']))
        this.apikey = tk.StringVar(value=config.get("APIkey"))

        entry['key'] = this.apikey.get()

        this.status['text'] = "Sending BGS data..."
        url = "https://ida-bgs.ztik.nl/api/input"
        r = requests.post(url, json=entry)
        if r.status_code == 200:
            sys.stderr.write("Status: 200\n")
            this.status['text'] = "Success: BGS data sent"
            t = threading.Timer(5.0, clearstatus)
        else:
            if r.status_code == 201:
                sys.stderr.write("Status: 201\n")
                this.status['text'] = "Success: BGS data n/a"
                t = threading.Timer(5.0, clearstatus)
            else:
                if r.status_code == 202:
                    sys.stderr.write("Status: 202\n")
                    this.status['text'] = "Success: API not ready"
                    t = threading.Timer(5.0, clearstatus)
                else:
                    data = json.loads(r.text)
                    sys.stderr.write("Status BGS: " + str(r.status_code) + ": " + str(data['message']) + "\n")
                    sys.stderr.write("Error BGS: " + str(data['error']) + "\n")
                    this.status['text'] = "Fail: " + str(r.status_code) + ": " + str(data['message'])
                    t = threading.Timer(10.0, clearstatus)
        t.start()


    elif entry['event'] == 'MissionCompleted':
        this.approvedatatransfer = tk.IntVar(value=config.getint("ADT"))
        if this.approvedatatransfer.get() == 1:
            # We completed a mission!
            this.apikey = tk.StringVar(value=config.get("APIkey"))

            entry['key'] = this.apikey.get()

            entry['Commodity'] = ''
            entry['Count'] = ''
            entry['Reward'] = ''
            entry['Donation'] = ''
            entry['Donated'] = ''
            entry['PermitsAwarded'] = ''
            entry['CommodityReward'] = ''
            entry['MaterialsReward'] = ''

            this.status['text'] = "Sending MSSN data..."
            url = "https://ida-bgs.ztik.nl/api/input"
            r = requests.post(url, json=entry)
            if r.status_code == 200:
                sys.stderr.write("Status: 200\n")
                this.status['text'] = "Success: MSSN data sent"
                t = threading.Timer(5.0, clearstatus)
            else:
                if r.status_code == 201:
                    sys.stderr.write("Status: 201\n")
                    this.status['text'] = "Success: MSSN data n/a"
                    t = threading.Timer(5.0, clearstatus)
                else:
                    if r.status_code == 202:
                        sys.stderr.write("Status: 202\n")
                        this.status['text'] = "Success: API not ready"
                        t = threading.Timer(5.0, clearstatus)
                    else:
                        data = json.loads(r.text)
                        sys.stderr.write("Status MSSN: " + str(r.status_code) + ": " + str(data['message']) + "\n")
                        sys.stderr.write("Error MSSN: " + str(data['error']) + "\n")
                        this.status['text'] = "Fail: " + str(r.status_code) + ": " + str(data['message'])
                        t = threading.Timer(10.0, clearstatus)
            t.start()

    elif entry['event'] == 'MultiSellExplorationData':
        this.approvedatatransfer = tk.IntVar(value=config.getint("ADT"))
        if this.approvedatatransfer.get() == 1:
            # We sold a page of exploration data!
            this.apikey = tk.StringVar(value=config.get("APIkey"))

            entry['key'] = this.apikey.get()
            entry['system'] = system
            entry['station'] = station

            this.status['text'] = "Sending EXPL data..."
            url = "https://ida-bgs.ztik.nl/api/input"
            r = requests.post(url, json=entry)
            if r.status_code == 200:
                sys.stderr.write("Status: 200\n")
                this.status['text'] = "Success: EXPL data sent"
                t = threading.Timer(5.0, clearstatus)
            else:
                if r.status_code == 201:
                    sys.stderr.write("Status: 201\n")
                    this.status['text'] = "Success: EXPL data n/a"
                    t = threading.Timer(5.0, clearstatus)
                else:
                    if r.status_code == 202:
                        sys.stderr.write("Status: 202\n")
                        this.status['text'] = "Success: API not ready"
                        t = threading.Timer(5.0, clearstatus)
                    else:
                        data = json.loads(r.text)
                        sys.stderr.write("Status EXPL: " + str(r.status_code) + ": " + str(data['message']) + "\n")
                        sys.stderr.write("Error EXPL: " + str(data['error']) + "\n")
                        this.status['text'] = "Fail: " + str(r.status_code) + ": " + str(data['message'])
                        t = threading.Timer(10.0, clearstatus)
            t.start()

    elif entry['event'] == 'SellExplorationData':
        this.approvedatatransfer = tk.IntVar(value=config.getint("ADT"))
        if this.approvedatatransfer.get() == 1:
            # We sold exploration data!
            this.apikey = tk.StringVar(value=config.get("APIkey"))

            entry['key'] = this.apikey.get()
            entry['system'] = system
            entry['station'] = station

            this.status['text'] = "Sending EXPL data..."
            url = "https://ida-bgs.ztik.nl/api/input"
            r = requests.post(url, json=entry)
            if r.status_code == 200:
                sys.stderr.write("Status: 200\n")
                this.status['text'] = "Success: EXPL data sent"
                t = threading.Timer(5.0, clearstatus)
            else:
                if r.status_code == 201:
                    sys.stderr.write("Status: 201\n")
                    this.status['text'] = "Success: EXPL data n/a"
                    t = threading.Timer(5.0, clearstatus)
                else:
                    if r.status_code == 202:
                        sys.stderr.write("Status: 202\n")
                        this.status['text'] = "Success: API not ready"
                        t = threading.Timer(5.0, clearstatus)
                    else:
                        data = json.loads(r.text)
                        sys.stderr.write("Status EXPL: " + str(r.status_code) + ": " + str(data['message']) + "\n")
                        sys.stderr.write("Error EXPL: " + str(data['error']) + "\n")
                        this.status['text'] = "Fail: " + str(r.status_code) + ": " + str(data['message'])
                        t = threading.Timer(10.0, clearstatus)
            t.start()

    elif entry['event'] == 'RedeemVoucher':
        this.approvedatatransfer = tk.IntVar(value=config.getint("ADT"))
        if this.approvedatatransfer.get() == 1:
            # We redeemed bond/bounty voucher!
            this.apikey = tk.StringVar(value=config.get("APIkey"))

            entry['key'] = this.apikey.get()
            entry['system'] = system
            entry['station'] = station
            if entry[''] == 'CombatBond':
              statustext = 'BOND';
            elif entry[''] == 'bounty':
              statustext = 'BNTY'

            this.status['text'] = "Sending " + statustext +" data..."
            url = "https://ida-bgs.ztik.nl/api/input"
            r = requests.post(url, json=entry)
            if r.status_code == 200:
                sys.stderr.write("Status: 200\n")
                this.status['text'] = "Success: " + statustext + " data sent"
                t = threading.Timer(5.0, clearstatus)
            else:
                if r.status_code == 201:
                    sys.stderr.write("Status: 201\n")
                    this.status['text'] = "Success: " + statustext + " data n/a"
                    t = threading.Timer(5.0, clearstatus)
                else:
                    if r.status_code == 202:
                        sys.stderr.write("Status: 202\n")
                        this.status['text'] = "Success: API not ready"
                        t = threading.Timer(5.0, clearstatus)
                    else:
                        data = json.loads(r.text)
                        sys.stderr.write("Status " + statustext + ": " + str(r.status_code) + ": " + str(data['message']) + "\n")
                        sys.stderr.write("Error " + statustext + ": " + str(data['error']) + "\n")
                        this.status['text'] = "Fail: " + str(r.status_code) + ": " + str(data['message'])
                        t = threading.Timer(10.0, clearstatus)
            t.start()

    elif entry['event'] == 'MarketSell':
        this.approvedatatransfer = tk.IntVar(value=config.getint("ADT"))
        if this.approvedatatransfer.get() == 1:
            # We sold commodities!
            this.apikey = tk.StringVar(value=config.get("APIkey"))

            entry['key'] = this.apikey.get()
            entry['system'] = system
            entry['station'] = station

            this.status['text'] = "Sending CRG data..."
            url = "https://ida-bgs.ztik.nl/api/input"
            r = requests.post(url, json=entry)
            if r.status_code == 200:
                sys.stderr.write("Status: 200\n")
                this.status['text'] = "Success: CRG data sent"
                t = threading.Timer(5.0, clearstatus)
            else:
                if r.status_code == 201:
                    sys.stderr.write("Status: 201\n")
                    this.status['text'] = "Success: CRG data n/a"
                    t = threading.Timer(5.0, clearstatus)
                else:
                    if r.status_code == 202:
                        sys.stderr.write("Status: 202\n")
                        this.status['text'] = "Success: API not ready"
                        t = threading.Timer(5.0, clearstatus)
                    else:
                        data = json.loads(r.text)
                        sys.stderr.write("Status CRG: " + str(r.status_code) + ": " + str(data['message']) + "\n")
                        sys.stderr.write("Error CRG: " + str(data['error']) + "\n")
                        this.status['text'] = "Fail: " + str(r.status_code) + ": " + str(data['message'])
                        t = threading.Timer(10.0, clearstatus)
            t.start()

    elif entry['event'] == 'MarketBuy':
        this.approvedatatransfer = tk.IntVar(value=config.getint("ADT"))
        if this.approvedatatransfer.get() == 1:
            # We bought commodities!
            this.apikey = tk.StringVar(value=config.get("APIkey"))

            entry['key'] = this.apikey.get()
            entry['system'] = system
            entry['station'] = station

            this.status['text'] = "Sending CRG data..."
            url = "https://ida-bgs.ztik.nl/api/input"
            r = requests.post(url, json=entry)
            if r.status_code == 200:
                sys.stderr.write("Status: 200\n")
                this.status['text'] = "Success: CRG data sent"
                t = threading.Timer(5.0, clearstatus)
            else:
                if r.status_code == 201:
                    sys.stderr.write("Status: 201\n")
                    this.status['text'] = "Success: CRG data n/a"
                    t = threading.Timer(5.0, clearstatus)
                else:
                    if r.status_code == 202:
                        sys.stderr.write("Status: 202\n")
                        this.status['text'] = "Success: API not ready"
                        t = threading.Timer(5.0, clearstatus)
                    else:
                        data = json.loads(r.text)
                        sys.stderr.write("Status CRG: " + str(r.status_code) + ": " + str(data['message']) + "\n")
                        sys.stderr.write("Error CRG: " + str(data['error']) + "\n")
                        this.status['text'] = "Fail: " + str(r.status_code) + ": " + str(data['message'])
                        t = threading.Timer(10.0, clearstatus)
            t.start()


def clearstatus():
    this.status['text'] = "Idle"