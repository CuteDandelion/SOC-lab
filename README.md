# Cybersecurity Threat Simulation and Response Workflow

This project integrates **Invoke-AtomicRunner** (from Atomic Red Team), **Splunk**, and **Node-RED** to create a robust cybersecurity workflow. It simulates adversarial activities, detects threats using enriched Sysmon logs, and automates responses. The setup leverages [Olaf Hartung's Sysmon configuration](https://github.com/olafhartong/sysmon-modular) to enrich Sysmon logs with MITRE ATT&CK information. Detection is based solely on Sysmon logs processed in Splunk using Sigma rules. Since this project uses Splunk’s free license, which does not support built-in alert actions, a Python script and the Splunk API are utilized to forward alerts to Node-RED.

*Note : This lab is still in progress & changes may still apply.

## Planned Lab Design

![Lab Overview](https://github.com/user-attachments/assets/d318bde9-c5d0-4b2f-92fd-19144a763e56)


## Prerequisites

- Basic knowledge of Windows administration, Sysmon, Splunk, Node-RED, and Python
- Windows operating system
- [Sysmon](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon) installed with [Olaf Hartung's configuration](https://github.com/olafhartong/sysmon-modular) for MITRE-enriched logs
- [Splunk Enterprise or Splunk Cloud](https://www.splunk.com/) instance with administrative access (free license)
- [Node-RED](https://nodered.org/) installed and running
- [Python 3.x](https://www.python.org/downloads/) installed
- [Splunk SDK for Python](https://dev.splunk.com/enterprise/docs/devtools/python/sdk-python/) installed (if required)
- [Git](https://git-scm.com/) installed

## Installation and Setup

1. **Clone the Repository**
   - Clone the project to your local machine:
     ```bash
     git clone https://github.com/CuteDandelion/SOC-lab.git
     cd SOC-lab.git
     ```
   - The repository includes:
     - **`AdversaryAttackEmulations`**: Contains scripts or configurations for simulating adversarial attacks using tools like Atomic Red Team to generate Sysmon logs for testing detection rules.
     - **`threathunting_sigma_rules`**: Stores Sigma rules for threat hunting and detection, which are converted to Splunk-compatible queries.
     - **`soar_alarm_bot.py`**: A polling script that queries Splunk for new alerts and forwards them to Node-RED via HTTP POST requests.
     - **`requirements.txt`**: Lists Python dependencies (e.g., Splunk SDK) required for the project. Install them with:
       ```bash
       pip install -r requirements.txt
       ```

2. **Set Up Sysmon**
   - Ensure Sysmon is installed on your Windows machine.
   - Download Olaf Hartung's Sysmon configuration and apply it:
     ```bash
     sysmon -accepteula -i path\to\olafhartung-sysmon-config.xml
     ```

3. **Configure Splunk**
   - Install the [Splunk Add-on for Microsoft Sysmon](https://splunkbase.splunk.com/app/1914/) if not already present.
   - Set up log forwarding from the Windows machine to Splunk to receive Sysmon logs.
   - Verify that Sysmon logs are being indexed in Splunk.

4. **Set Up Node-RED**
   - Install Node-RED if not already installed:
     ```bash
     npm install -g node-red
     ```
   - Start Node-RED:
     ```bash
     node-red
     ```
   - Import the provided Node-RED flows from the repository:
     - Open the Node-RED web interface (typically `http://localhost:1880`)
     - Go to Menu > Import > Select the flow file from the repository

5. **Set Up Atomic Red Team**
   - Install Atomic Red Team if not already installed:
     ```powershell
     IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing); Install-AtomicRedTeam -getAtomics
     ```
   - Configure Invoke-AtomicRunner (used in `AdversaryAttackEmulations`) to execute specific test cases that generate Sysmon logs.

6. **Set Up Sigma for Threat Detection**
   - Install `sigma-cli` and the Splunk backend plugin:
     ```bash
     pip install sigma-cli
     sigma plugin install splunk
     ```
   - Convert Sigma rules from `threathunting_sigma_rules` to Splunk queries:
     ```bash
     sigma convert --target splunk --pipeline splunk threathunting_sigma_rules/your_rule.yml
     ```
   - Copy the generated Splunk query into your Splunk search interface.

7. **Set Up Python Script for Splunk API Integration**
   - Note that splunk with free license does not require logging in.
   - The script is still in testing and subject to be changed.
   - Configure `soar_alarm_bot.py` to connect to your Splunk instance:
     - Set the Splunk API endpoint (e.g., `https://localhost:8089`).
     - Define the search query to retrieve Sigma-based alerts (e.g., `search index=sysmon sigma=*`).
   - Configure the script to forward alerts to Node-RED:
     - Set the Node-RED endpoint (e.g., `http://localhost:1880/sigma-alerts`).
     - Ensure the script sends alerts as HTTP POST requests to Node-RED.

8. **Run the Python Script**
   - Execute `soar_alarm_bot.py` to start polling Splunk for new alerts:
     ```bash
     python soar_alarm_bot.py
     ```
   - The script will periodically query Splunk and forward alerts to Node-RED.

## Usage

1. **Run Threat Simulations**
   - Execute specific Atomic tests using Invoke-AtomicRunner from `AdversaryAttackEmulations`:
     ```powershell
     Invoke-AtomicTest T1003 -TestNumbers 1
     ```
   - This simulates an adversarial technique, generating enriched Sysmon logs.

2. **Monitor in Splunk**
   - View forwarded Sysmon logs in Splunk's search interface.
   - Use Sigma rules from `threathunting_sigma_rules` or custom SPL queries to detect simulated threats.

3. **Forward Alerts to Node-RED**
   - The `soar_alarm_bot.py` script queries Splunk via the API for new alerts and forwards them to Node-RED via HTTP POST requests.

4. **Automate Responses with Node-RED**
   - Node-RED receives the alerts and executes predefined flows to respond (e.g., isolating a host or sending notifications).

## Workflow Explanation

1. **Threat Simulation**: Invoke-AtomicRunner generates Sysmon logs enriched with MITRE ATT&CK data.
2. **Log Forwarding**: Sysmon logs are sent to Splunk for analysis.
3. **Threat Detection**: Splunk uses Sigma rules and SPL queries to identify threats.
4. **Alert Forwarding**: A Python script queries Splunk via the API and forwards alerts to Node-RED.
5. **Automated Response**: Node-RED processes the alerts and executes response flows.

## Resources

- [Sysmon Documentation](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)
- [Splunk Documentation](https://docs.splunk.com/Documentation)
- [Node-RED Documentation](https://nodered.org/docs/)
- [Atomic Red Team GitHub](https://github.com/redcanaryco/atomic-red-team)
- [Olaf Hartung's Sysmon Configuration](https://github.com/olafhartong/sysmon-modular)
- [Splunk SDK for Python](https://dev.splunk.com/enterprise/docs/devtools/python/sdk-python/)
