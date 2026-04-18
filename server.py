import socket
import json
import os
import threading
import time

# --- 1. CONFIGURATION (Must match Agent) ---
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5000
UDP_PORT = 5001
SECRET_KEY = "ELECON_DISCOVERY_2026"

def start_beacon():
    """Shouts 'I am the Admin Server' every 5 seconds to wake up Agents."""
    beacon_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    beacon_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    print(f"[*] Discovery Beacon Active on UDP {UDP_PORT}")
    while True:
        beacon_socket.sendto(SECRET_KEY.encode('utf-8'), ('<broadcast>', UDP_PORT))
        time.sleep(5)

def start_server():
    print("=============================================")
    print("    SERVER IS ON    ")
    print("=============================================\n")

    # Start the discovery beacon in a separate thread
    threading.Thread(target=start_beacon, daemon=True).start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Could not start server on port {SERVER_PORT}: {e}")
        return

    server_socket.listen(15)
    print(f"📡 Server Online. Waiting for Agents to report...\n")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"🔗 Incoming connection from {client_address[0]}")

            try:
                data_str = ""
                # Receive the full snapshot data
                while True:
                    packet = client_socket.recv(4096)
                    if not packet: break
                    data_str += packet.decode('utf-8')

                if data_str:
                    data_json = json.loads(data_str)
                    # Use Node Name for filename
                    pc_name = data_json['system_info'].get('Node Name', 'Unknown_PC')
                    filename = f"scan_results_{pc_name}.json"
                    
                    with open(filename, "w") as f:
                        json.dump(data_json, f, indent=4)
                    
                    print(f"✅ SNAPSHOT RECEIVED: '{pc_name}' audit saved to disk.")
                    print(f"   (Data stored in {filename})\n")
            
            except Exception as e:
                print(f"⚠️ Error processing snapshot from {client_address[0]}: {e}")
            finally:
                client_socket.close()

    except KeyboardInterrupt:
        print("\n🛑 Stopping Server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()