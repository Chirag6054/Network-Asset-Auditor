import platform
import socket
import psutil
import json
import uuid
import subprocess
import wmi
import os
import winreg
import time
from datetime import datetime

# --- CONFIGURATION FOR AUTO-DISCOVERY ---
UDP_PORT = 5001
SECRET_KEY = ""

def get_size(bytes, suffix="B"):
    bytes = abs(float(bytes)) 
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor: return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_device_type():
    try:
        c = wmi.WMI()
        if len(c.Win32_SystemEnclosure()) > 0:
            chassis_code = c.Win32_SystemEnclosure()[0].ChassisTypes[0]
            if chassis_code in [8, 9, 10, 11, 12, 14, 18, 21, 30, 31, 32]: return "Laptop"
            elif chassis_code in [3, 4, 6, 7, 13, 15, 16, 19, 20, 22, 23, 24]: return "Desktop"
    except: pass
    return "Unknown Device"

def get_windows_license_info():
    os_name = platform.system() + " " + platform.release()
    status = "Check Required (Run as Admin)"
    try:
        c = wmi.WMI()
        os_name = c.Win32_OperatingSystem()[0].Caption
        cmd = 'powershell "(Get-WmiObject -query \'select * from SoftwareLicensingProduct where LicenseStatus=1\').Name"'
        output = subprocess.check_output(cmd, shell=True).decode(errors='ignore')
        if "Windows" in output:
            status = "Licensed/Activated"
        else:
            status = "Unlicensed/Trial"
    except: pass
    return os_name, status

def get_deep_hardware():
    data = {"GPU": [], "RAM_Sticks": [], "Processor_Specs": {"Name": "Unknown", "MaxClockSpeed": "Unknown"}}
    try:
        c = wmi.WMI()
        if len(c.Win32_BaseBoard()) > 0:
            board = c.Win32_BaseBoard()[0]
            data['Motherboard'] = {"Manufacturer": board.Manufacturer, "Product": board.Product, "Serial": board.SerialNumber}
        
        for gpu in c.Win32_VideoController():
            gpu_name = gpu.Name
            vram = "Unknown"
            if "NVIDIA" in gpu_name.upper():
                try:
                    smi_output = subprocess.check_output('nvidia-smi --query-gpu=memory.total --format=csv,noheader', shell=True).decode().strip()
                    if "MiB" in smi_output:
                        mib_val = float(smi_output.replace("MiB", "").strip())
                        vram = f"{round(mib_val / 1024, 2)} GB (Dedicated)"
                    else:
                        vram = smi_output
                except:
                    vram = "Check Task Manager (>4GB Limit)"
            else:
                raw_vram = abs(float(gpu.AdapterRAM)) if gpu.AdapterRAM else 0
                gb_vram = round(raw_vram / (1024**3), 2)
                vram = f"{gb_vram} GB (Dedicated)"
                
            data['GPU'].append({"Name": gpu_name, "DriverVersion": gpu.DriverVersion, "Capacity": vram})
        
        for stick in c.Win32_PhysicalMemory():
            data['RAM_Sticks'].append({"Capacity": get_size(int(stick.Capacity)), "Manufacturer": stick.Manufacturer, "Speed": f"{stick.Speed}MHz"})
            
        proc = c.Win32_Processor()[0]
        data['Processor_Specs'] = {"Name": proc.Name.strip(), "MaxClockSpeed": f"{proc.MaxClockSpeed}MHz"}
    except: pass
    return data

def get_security_status():
    sec_data = {"Open_Ports": [], "Firewall_Status": "Unknown"}
    try:
        connections = psutil.net_connections(kind='inet')
        seen_ports = set()
        for conn in connections:
            if conn.status == 'LISTEN':
                port = conn.laddr.port
                if port not in seen_ports:
                    seen_ports.add(port)
                    pid = conn.pid
                    proc_name = "Unknown"
                    if pid:
                        try: proc_name = psutil.Process(pid).name()
                        except: pass
                    sec_data["Open_Ports"].append({"Port": port, "Process": proc_name, "PID": pid})
        
        sec_data["Open_Ports"] = sorted(sec_data["Open_Ports"], key=lambda x: x['Port'])
    except: pass
    
    try:
        cmd = "netsh advfirewall show allprofiles state"
        output = subprocess.check_output(cmd, shell=True).decode()
        sec_data["Firewall_Status"] = "Active (ON)" if "ON" in output else "DISABLED (High Risk)"
    except: sec_data["Firewall_Status"] = "Check Failed"
    return sec_data

def determine_license(name):
    name_lower = str(name).lower()
    if any(x in name_lower for x in ['free', 'open source', 'community', 'player']): return "Free"
    return "Licensed / Commercial"

def get_all_software_and_services():
    software_list = []
    services_list = []
    
    try:
        ps_cmd = r"""powershell "Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*, HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*, HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion | Where-Object {$_.DisplayName -ne $null}" """
        process = subprocess.Popen(ps_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = process.communicate()
        if stdout:
            lines = stdout.decode(errors='ignore').split('\r\n')
            for line in lines[3:]: 
                if line.strip():
                    parts = line.split("  ") 
                    name = parts[0].strip()
                    if name:
                        software_list.append({"Name": name, "Version": "Installed", "Type": "User App", "License_Type": determine_license(name)})
    except: pass

    try:
        ps_cmd2 = 'powershell "Get-AppxPackage | Select-Object Name"'
        process2 = subprocess.Popen(ps_cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout2, _ = process2.communicate()
        if stdout2:
            lines = stdout2.decode(errors='ignore').split('\r\n')
            for line in lines[3:]:
                name = line.strip()
                if name:
                    software_list.append({"Name": name, "Version": "Inbuilt", "Type": "Windows App", "License_Type": "Free"})
    except: pass

    try:
        c = wmi.WMI()
        for service in c.Win32_Service():
            services_list.append({"Name": service.DisplayName, "State": service.State, "Status": service.Status})
    except: pass
    
    return software_list, services_list

def scan_pc():
    # Message updated per your request
    print("[*] Extracting information... please wait.")
    uname = platform.uname()
    os_name, os_status = get_windows_license_info()
    
    sys_info = {
        "Node Name": uname.node, 
        "OS_Name": os_name, 
        "OS_License": os_status,
        "Release": uname.release, 
        "Processor": uname.processor, 
        "Device_Type": get_device_type()
    }
    
    cpu_info = {"Physical_Cores": psutil.cpu_count(logical=False), "Total_Cores": psutil.cpu_count(logical=True)}
    svmem = psutil.virtual_memory()
    memory_info = {"Total": get_size(svmem.total), "Used_Percent": f"{svmem.percent}%"}
    disk_info = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({"Device": partition.device, "Total_Size": get_size(usage.total), "Free": get_size(usage.free), "Percentage": f"{usage.percent}%"})
        except: continue
        
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
    
    apps, services = get_all_software_and_services()
    
    return {
        "scan_timestamp": str(datetime.now()), 
        "system_info": sys_info, 
        "deep_hardware": get_deep_hardware(),
        "security_info": get_security_status(), 
        "cpu_info": cpu_info, 
        "memory_info": memory_info,
        "disk_info": disk_info, 
        "network_info": {"IP_Address": ip_address, "MAC_Address": mac_address},
        "installed_software": apps,
        "system_services": services
    }

if __name__ == "__main__":
    # --- AUTO-DISCOVERY ---
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('', UDP_PORT))
    
    print("---------------------------------------------")
    print("      NETWORK AUDIT AGENT INITIALIZED       ")
    print("---------------------------------------------")
    print("Status: Waiting for Admin Discovery signal...")

    # Removed while True loop to make it a one-time operation per manual run
    try:
        # Wait for the UDP broadcast signal
        data, addr = udp_socket.recvfrom(1024)
        if data.decode('utf-8') == SECRET_KEY:
            admin_ip = addr[0]
            print(f"\n[+] Admin Found at {admin_ip}! Starting scan...")
            
            # Perform the scan
            data_to_send = scan_pc()
            
            # Connect via TCP to send the data
            try:
                print("📡 Delivering report to Admin Server...")
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(15) 
                client_socket.connect((admin_ip, 5000))
                client_socket.sendall(json.dumps(data_to_send).encode('utf-8'))
                client_socket.close()
                print("\n✅ SUCCESS: Report delivered successfully!")
            except Exception as e:
                print(f"\n❌ FAILED to deliver report: {e}")
                
    except Exception as e:
        print(f"\n❌ Error during discovery: {e}")
    finally:
        udp_socket.close()

    # Keeps the CMD window open so you can see the results
    print("\n" + "="*45)
    print("Audit process finished.")
    input("Press [ENTER] to exit the application...")