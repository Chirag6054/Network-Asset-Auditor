import streamlit as st
import pandas as pd
import json
import glob
import os
import io
from datetime import datetime

# --- NEW: EXCEL GENERATOR (Replaces PDF logic) ---
def generate_excel_report(data):
    output = io.BytesIO()
    # Engine requires xlsxwriter: pip install xlsxwriter
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # 1. Summary Sheet
        sys = data.get('system_info', {})
        net = data.get('network_info', {})
        summary_df = pd.DataFrame({
            "Field": ["Device Name", "OS Name", "License", "IP Address", "MAC Address", "Device Type"],
            "Value": [
                sys.get('Node Name'), sys.get('OS_Name'), sys.get('OS_License'),
                net.get('IP_Address'), net.get('MAC_Address'), sys.get('Device_Type')
            ]
        })
        summary_df.to_excel(writer, index=False, sheet_name='System_Summary')

        # 2. Software Sheet
        if data.get('installed_software'):
            pd.DataFrame(data['installed_software']).to_excel(writer, index=False, sheet_name='Software_Inventory')

        # 3. Services Sheet
        if data.get('system_services'):
            pd.DataFrame(data['system_services']).to_excel(writer, index=False, sheet_name='System_Services')

        # 4. Security & Ports Sheet
        sec = data.get('security_info', {})
        if sec.get('Open_Ports'):
            pd.DataFrame(sec['Open_Ports']).to_excel(writer, index=False, sheet_name='Security_Ports')

        # Formatting
        workbook = writer.book
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        for sheet in writer.sheets.values():
            sheet.set_column(0, 10, 25)
            
    return output.getvalue()

# CONFIGURATION
st.set_page_config(page_title="Network Asset Intelligence", layout="wide")

# --- UI LAYOUT ---
col_title, col_download = st.columns([3, 1])
with col_title:
    st.title("Network Asset & Security Auditor")

st.markdown("---")

# Handling One-Time Snapshots
json_files = glob.glob("scan_results_*.json")

if not json_files:
    st.warning("No scan reports found. Ensure Agents have discovered the server.")
else:
    device_map = {f.replace("scan_results_", "").replace(".json", ""): f for f in json_files}
    selected_label = st.sidebar.selectbox("Select Device to Inspect:", list(device_map.keys()))
    
    with open(device_map[selected_label], 'r') as f:
        data = json.load(f)

    with col_download:
        st.write("") 
        # Update: PDF to Excel
        excel_bytes = generate_excel_report(data)
        st.download_button(
            label="📊 Download Full Audit Excel",
            data=excel_bytes,
            file_name=f"Full_Audit_{selected_label}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown("### Device Identity")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.caption("Device Name")
        st.write(f"**{data['system_info'].get('Node Name', 'Unknown')}**")
    with c2:
        st.caption("Device Type")
        st.write(f"**{data['system_info'].get('Device_Type', 'Unknown')}**")
    with c3:
        st.caption("IP Address")
        st.write(f"**{data['network_info'].get('IP_Address', 'Unknown')}**")
    with c4:
        st.caption("MAC Address")
        st.write(f"**{data['network_info'].get('MAC_Address', 'Unknown')}**")

    st.markdown("---")

    # TABS (Format preserved exactly)
    tab_win, tab1, tab2, tab3, tab4 = st.tabs(["Windows Details", "Deep Hardware", "Software Inventory", "Security Audit", "Resources"])

    with tab_win:
        st.subheader("Operating System & Licensing")
        w1, w2, w3 = st.columns(3)
        with w1:
            st.caption("OS Version")
            st.write(f"**{data['system_info'].get('OS_Name', 'Unknown')}**")
        with w2:
            st.caption("Release")
            st.write(f"**{data['system_info'].get('Release', 'Unknown')}**")
        with w3:
            st.caption("License Status")
            st.write(f"**{data['system_info'].get('OS_License', 'Unknown')}**")

    with tab1:
        st.subheader("Motherboard & RAM Identity")
        mb = data.get('deep_hardware', {}).get('Motherboard', {})
        col_mb1, col_mb2, col_mb3 = st.columns(3)
        col_mb1.metric("Manufacturer", mb.get("Manufacturer", "Unknown"))
        col_mb2.metric("Product ID", mb.get("Product", "Unknown"))
        col_mb3.metric("Serial Number", mb.get("Serial", "Unknown"))
        
        st.markdown("---")
        st.caption("Physical RAM Sticks")
        st.dataframe(data.get('deep_hardware', {}).get('RAM_Sticks', []), use_container_width=True)

        st.markdown("---")
        st.subheader("Processor & Graphics Specs")
        hw1, hw2 = st.columns(2)
        with hw1:
            st.write("#### CPU Model")
            st.info(data.get('deep_hardware', {}).get('Processor_Specs', {}).get('Name', data['system_info'].get('Processor', 'Unknown')))
        with hw2:
            st.write("#### Graphics Card (GPU)")
            st.table(data.get('deep_hardware', {}).get('GPU', []))

    with tab2:
        st.subheader("Installed & Inbuilt Applications")
        sub_apps, sub_serv = st.tabs(["Apps", "Services"])
        
        with sub_apps:
            soft_list = data.get('installed_software', [])
            if soft_list:
                df_soft = pd.DataFrame(soft_list)
                col_map = {"Name": "Name", "Version": "Version", "Type": "Installed / Inbuilt", "License_Type": "License Type"}
                df_display = df_soft.rename(columns=col_map)
                
                search = st.text_input("Search Software (e.g., Valorant, Notepad)", "")
                if search:
                    df_display = df_display[df_display['Name'].str.contains(search, case=False, na=False)]
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)

        with sub_serv:
            st.write("#### Background Services")
            serv_list = data.get('system_services', [])
            if serv_list:
                df_serv = pd.DataFrame(serv_list)
                search_s = st.text_input("Search Services", "")
                if search_s:
                    df_serv = df_serv[df_serv['Name'].str.contains(search_s, case=False, na=False)]
                st.dataframe(df_serv, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Security Posture")
        fw_status = data['security_info']['Firewall_Status']
        if "ON" in fw_status:
            st.success(f"Firewall: {fw_status}")
        else:
            st.error(f"Firewall: {fw_status}")
            
        st.write("#### Open Ports (Listening)")
        ports_data = data['security_info']['Open_Ports']
        if ports_data:
            df_ports = pd.DataFrame(ports_data)
            def analyze_risk(port):
                return "HIGH RISK" if port in [21, 23, 445, 3389] else "Normal"
            if 'Port' in df_ports.columns:
                df_ports['Risk Level'] = df_ports['Port'].apply(analyze_risk)
            st.dataframe(df_ports, use_container_width=True, hide_index=True)
        else:
            st.success("No open ports detected.")

    with tab4:
        st.subheader("System Resources")
        m1, m2, m3 = st.columns(3)
        m1.metric("CPU Cores", data['cpu_info']['Physical_Cores'])
        m2.metric("Total RAM", data['memory_info']['Total'])
        m3.metric("RAM Used", data['memory_info'].get('Used_Percent', 'N/A'))
        
        st.write("#### Storage Partitions")
        df_disk = pd.DataFrame(data['disk_info'])
        st.dataframe(df_disk, hide_index=True)