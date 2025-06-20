#Note: This is Experimental, changes may still apply
#Description: Forward splunk query result to Node Red flow automation tool / SOAR via webhook

import requests
import json
import time
import urllib3
import argparse
import subprocess
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def run_search():
    res = requests.post(
        f"{SPLUNK_HOST}/services/search/jobs",
        data={
            "search": SPL_QUERY, 
            "earliest_time":TIME_RANGE["earliest_time"],
            "latest_time":TIME_RANGE["latest_time"],
            "output_mode": "json"
        },
        verify=False
    )
    sid = res.json()['sid']
    return sid

def get_results(sid):
    url = f"{SPLUNK_HOST}/services/search/jobs/{sid}/results?output_mode=json"
    for _ in range(10):  # wait for completion
        r = requests.get(url,  verify=False)
        if r.status_code == 200:
            results = r.json().get("results", [])
            return results
        time.sleep(1)
    return []

def post_to_node_red(data):
    requests.post(NODE_RED_WEBHOOK, json=data)


def main():
     #while True:
        try:
            sid = run_search()
            results = get_results(sid)
            if results:
                print(results[0])
                post_to_node_red(results[0])  # send only first match
        except Exception as e:
            print(f"Error: {e}")
        #time.sleep(60)  # check every 1 minute

if __name__ == "__main__":
   
   SPLUNK_HOST = "https://localhost:8089"
   SPL_QUERY = ""
   NODE_RED_WEBHOOK = "http://localhost:1880/sigma-alert"

   #Configure splunk search Timeframe : last 15 mins
   TIME_RANGE = {
       "earliest_time": "-15m@m",
       "latest_time": "now"
   }

   parser = argparse.ArgumentParser(description="program for forwarding SPLUNK alarm to Node-RED")
   parser.add_argument("path", type=str, help="provide sigma-rule file")

   args = parser.parse_args()
   
   command = ['sigma','convert','--target','splunk','--pipeline','splunk_windows',args.path]
   
   #Run Sigma Conversion
   process = subprocess.Popen(
        command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
   stdout, err = process.communicate()

   if process.returncode == 0:
       SPL_QUERY = "search " + stdout
       print(SPL_QUERY)
   else:
       print(err)
       sys.exit(1)

   #sys.exit()
   main()
