# Network Asset & Security Auditor

This project is a distributed enterprise-grade auditing ecosystem developed during a 16-week industrial internship at TechElecon Private Limited. The system automates the tracking of corporate IT assets and identifies endpoint security vulnerabilities to replace manual, error-prone tracking methodologies.

---

## Project Overview

The Network Asset & Security Auditor was engineered to address the "Manual Burden" and "Shadow IT" risks associated with large-scale network management. The system consists of lightweight Python agents that interrogate endpoints and transmit data to a centralized ingestion server for visualization on an analytical dashboard.

---

## Key Features

### Hardware Interrogation
* **Granular Extraction:** The system automatically pulls motherboard serials, RAM frequencies, and CPU clock limits via the Windows Management Instrumentation (WMI) library.
* **NVIDIA-SMI Fallback:** It implements a specialized fallback routine to execute nvidia-smi, circumventing 32-bit integer overflow bugs in standard WMI queries to ensure 100% accurate GPU VRAM reporting.
* **Device Identification:** The agent utilizes chassis codes to automatically distinguish between laptops and desktops.

### Software Inventory and Compliance
* **Registry-Based Scanning:** The system scans both HKLM and HKCU registry hives to capture user-level installations and "Shadow IT" apps often missed by standard tools.
* **Windows Store Audit:** It executes PowerShell commands to inventory built-in AppxPackages.
* **License Verification:** The agent securely queries OS activation status to ensure enterprise policy compliance.

### Security and Threat Mapping
* **Port-to-PID Mapping:** The system utilizes the psutil library to scan active network sockets and map listening ports directly to their specific Process IDs (PIDs) and executable names.
* **Firewall Monitoring:** It provides real-time extraction of Windows Defender firewall states across Domain, Private, and Public profiles.

### Administrative Reporting
* **Reactive UI Engine:** The dashboard is built on the Streamlit framework and uses Pandas DataFrames to render interactive, searchable tables.
* **Excel Reporting Engine:** The system generates searchable, multi-sheet Master Excel reports to ensure data portability and administrative compliance.

---

## Technology Stack

* **Core Language:** Python 3.11.
* **System Discovery:** WMI and Winreg for hardware and registry manipulation.
* **Networking:** TCP/IP Sockets for data transmission (Port 5000) and UDP Broadcast for auto-discovery (Port 5001).
* **Resource Monitoring:** psutil for resource utilization and network socket mappings.
* **Frontend and Reporting:** Streamlit, Pandas, and XlsxWriter.
* **Compilation:** PyInstaller for standalone executable generation.

---

## System Architecture

The system follows a unidirectional push model to harden endpoint security by keeping inbound ports closed on employee workstations.

1. **The Agent (agent.exe):** A lightweight interrogation engine deployed on workstations that collects system telemetry.
2. **The Socket Server (server.exe):** A centralized listener that captures incoming JSON payloads in secure 4096-byte chunks to prevent memory overflow.
3. **The Dashboard (dashboard.py):** A management interface that reads processed JSON snapshots and provides a searchable overview of the network infrastructure.


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

---

## Acknowledgments

* **TechElecon Private Limited:** For providing the internship opportunity and professional environment.
* **Mr. Nilesh Prajapati (Company Mentor):** For technical insights and guidance throughout the project development.
* **Prof. Sneh Vyas (Internal Guide):** For academic support and feedback during the project lifecycle.
