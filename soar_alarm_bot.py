#Note: This is Experimental
#Description: Forward splunk query result to Node Red flow automation tool / SOAR via webhook

import requests
import json
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPLUNK_HOST = "https://localhost:8089"
SPL_QUERY = """search index="sysmon" source="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational" EventID=1 Image="*\\cmd.exe" OR OriginalFileName="Cmd.Exe" CommandLine IN ("*iwr*", "*Invoke-WebRequest*", "*https://github.com/redcanaryco/atomic-red-team/*", "*c:\\Atomic.dll*") | head 1 """
NODE_RED_WEBHOOK = "http://localhost:1880/sigma-alert"


def run_search():
    res = requests.post(
        f"{SPLUNK_HOST}/services/search/jobs",
        data={"search": SPL_QUERY, "output_mode": "json"},
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

if __name__ == "__main__":
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
