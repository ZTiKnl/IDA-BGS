# IDA-BGS
An EDMC plugin that gathers system/faction data for specific systems and sends JSON formatted data to webapi

# How to use:
1. Clone the repo to the EDMC plugin folder, or download the load.py file to a new folder inside the EDMC plugin folder
   (default: `c:\Users\%USERNAME%\AppData\Local\EDMarketConnector\plugins`)
2. Request API key on webinterface
3. Start up EDMC
4. Insert API key into plugin by going to File -> Settings, tab IDA-BGS, enter/paste the key, and hit OK

There is an extra row in the main window of EDMC, labeled IDA-BGS.  
This row can have 4 different values:  
-Idle  
  Not doing anything, waiting for FSDjump event to be triggered  
-Success (no data sent)  
  Just processed FSDjump event, but destination system does not contain our faction  
-Success (data sent)  
  Just processed FSDjump event, our faction is present here, data sent without errors  
-Fail: error code - short error message  
  could be many things, the error code and short error message will be a hint/clue  
  The real error can be found in EDMC log file, usually located in `%TMP%/EDMarketConnector.log`  


# What it does:
Whenever a user jumps from one system to another, upon landing in the destination system, an event is created in the ED journal file.  
This plugin reads this event (FSDjump), and ONLY this event, gathers system/faction data, and pushes JSON formatted data to a webapi.  
The webapi can be found in another repo (coming soon)

# Changes to make for use by another faction
Want to make this work for another faction, all you need to change here are 2 instances of 'IDA-BGS' and 2 instances of the server url to push data to (https://ida-bgs.ztik.nl/api.php)  
One more change will be required for the webapi, which does the filtering of systems where the faction has a presence or not