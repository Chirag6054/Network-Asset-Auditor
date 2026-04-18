# Network Asset & Security Auditor

[cite_start]This project is a distributed enterprise-grade auditing ecosystem developed during a 16-week industrial internship at TechElecon Private Limited[cite: 17, 258]. [cite_start]The system automates the tracking of corporate IT assets and identifies endpoint security vulnerabilities to replace manual, error-prone tracking methodologies[cite: 25, 261].

---

## Project Overview

[cite_start]The Network Asset & Security Auditor was engineered to address the "Manual Burden" and "Shadow IT" risks associated with large-scale network management[cite: 25, 26, 261]. [cite_start]The system consists of lightweight Python agents that interrogate endpoints and transmit data to a centralized ingestion server for visualization on an analytical dashboard[cite: 30, 31, 262].

---

## Key Features

### Hardware Interrogation
* [cite_start]**Granular Extraction:** The system automatically pulls motherboard serials, RAM frequencies, and CPU clock limits via the Windows Management Instrumentation (WMI) library[cite: 33, 282, 405].
* [cite_start]**NVIDIA-SMI Fallback:** It implements a specialized fallback routine to execute nvidia-smi, circumventing 32-bit integer overflow bugs in standard WMI queries to ensure 100% accurate GPU VRAM reporting[cite: 62, 283, 460].
* **Device Identification:** The agent utilizes chassis codes to automatically distinguish between laptops and desktops.

### Software Inventory and Compliance
* [cite_start]**Registry-Based Scanning:** The system scans both HKLM and HKCU registry hives to capture user-level installations and "Shadow IT" apps often missed by standard tools[cite: 284, 363, 459].
* [cite_start]**Windows Store Audit:** It executes PowerShell commands to inventory built-in AppxPackages[cite: 64, 407, 491].
* [cite_start]**License Verification:** The agent securely queries OS activation status to ensure enterprise policy compliance[cite: 62, 291, 365].

### Security and Threat Mapping
* [cite_start]**Port-to-PID Mapping:** The system utilizes the psutil library to scan active network sockets and map listening ports directly to their specific Process IDs (PIDs) and executable names[cite: 66, 290, 411].
* [cite_start]**Firewall Monitoring:** It provides real-time extraction of Windows Defender firewall states across Domain, Private, and Public profiles[cite: 45, 289, 412].

### Administrative Reporting
* [cite_start]**Reactive UI Engine:** The dashboard is built on the Streamlit framework and uses Pandas DataFrames to render interactive, searchable tables[cite: 36, 303, 420].
* **Excel Reporting Engine:** The system generates searchable, multi-sheet Master Excel reports to ensure data portability and administrative compliance.

---

## Technology Stack

* [cite_start]**Core Language:** Python 3.11[cite: 309, 450].
* [cite_start]**System Discovery:** WMI and Winreg for hardware and registry manipulation[cite: 39, 312].
* **Networking:** TCP/IP Sockets for data transmission (Port 5000) and UDP Broadcast for auto-discovery (Port 5001).
* [cite_start]**Resource Monitoring:** psutil for resource utilization and network socket mappings[cite: 313, 597].
* **Frontend and Reporting:** Streamlit, Pandas, and XlsxWriter.
* [cite_start]**Compilation:** PyInstaller for standalone executable generation[cite: 315, 454].

---

## System Architecture

[cite_start]The system follows a unidirectional push model to harden endpoint security by keeping inbound ports closed on employee workstations[cite: 424, 425].

1. [cite_start]**The Agent (agent.exe):** A lightweight interrogation engine deployed on workstations that collects system telemetry[cite: 347, 402].
2. [cite_start]**The Socket Server (server.exe):** A centralized listener that captures incoming JSON payloads in secure 4096-byte chunks to prevent memory overflow[cite: 297, 354, 416].
3. [cite_start]**The Dashboard (dashboard.py):** A management interface that reads processed JSON snapshots and provides a searchable overview of the network infrastructure[cite: 301, 357, 418].



[Image of client-server architecture]


---

## Installation and Usage

### Prerequisites
The system requires Python 3.11 and the dependencies listed in `requirements.txt`.

### Setup Instructions
1. **Clone the repository:**
   `git clone https://github.com/Chirag6054/Network-Asset-Auditor.git`
2. **Install dependencies:**
   `pip install -r requirements.txt`
3. **Start the Server:**
   `python server.py`
4. **Deploy the Agent:**
   Execute `agent.py` or the compiled `agent.exe` on network workstations to transmit audit data.
5. **Launch the Dashboard:**
   `streamlit run dashboard.py`
