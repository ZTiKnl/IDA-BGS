# IDA-BGS
An EDMC plugin that gathers system/faction data for specific systems and sends JSON formatted data to webapi

# How to use:
1. Clone the repo to the EDMC plugin folder, or download the load.py file to a new folder inside the EDMC plugin folder
   (default: c:\Users\%USERNAME%\AppData\Local\EDMarketConnector\plugins\)
2. Request API key on webinterface
3. Start up EDMC
4. Insert API key into plugin by going to File -> Settings, tab IDA-BGS, enter/paste the key, and hit OK

# What it does:
Whenever a user jumps from one system to another, upon landing in the destination system, an event is created in the ED journal file.
This plugin reads that event (FSDjump), and ONLY that event, gathers system/faction data, and pushes it to a webapi.
The webapi can be found in another repo (coming soon)


