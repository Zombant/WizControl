import socket
import json
from time import sleep
import sys

# Import IP addresses from json file
with open("ip_addresses.json", "r") as f:
    ip_addresses = dict(json.load(f))

scenes = {
    "cozy": 6,
    "warm_white": 11,
    "daylight": 12,
    "cool_white": 13,
    "night_light": 14,
    "focus": 15,
    "relax": 16,
    "true_colors": 17,
    "tv_time": 18,
    "plant_growth": 19 }

    

def send_command(message, ip, port=38899, retries=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    
    for attempt in range(retries):
        try:
            sock.sendto(json.dumps(message).encode(), (ip, port))
            response, addr = sock.recvfrom(1024)
            return json.loads(response.decode())
        except socket.timeout:
            print(f"Timeout occurred, retrying... ({attempt + 1}/{retries})")
        except Exception as e:
            print(f"Error sending command: {e}")
            return None

    sock.close()
    print(f"Failed to send command after {retries} retries")
    return None
        

def set_light_state(ip, state):
    message = {
        "method": "setState",
        "params": {"state": state}
    }

    send_command(message, ip)
    

def set_light_rgb(ip, r, g, b, dimming=100):
    message = {
        "method": "setPilot",
        "params": { "r": r,
                    "g": g,
                    "b": b,
                    "dimming": dimming}
    }
    
    send_command(message, ip)

def set_light_temp(ip, temp, dimming=100):
    message = {
        "method": "setPilot",
        "params": { "temp": temp,
                    "dimming": dimming}
    }
    
    send_command(message, ip)

def set_light_scene(ip, scene_id, dimming=100):
    message = {
        "method": "setPilot",
        "params": { "sceneId": scene_id,
                    "dimming": dimming}
    }

    send_command(message, ip)

def get_light_status(ip):
    message = {
        "method": "getPilot",
        "params": { }
    }

    return send_command(message, ip)

def list_devices():
    for name, _ in ip_addresses.items():
        print(name)

def list_scenes():
    for name, _ in scenes.items():
        print(name)

def print_help():
    print(f"Usage: python {sys.argv[0]} <device> <action> [args]\n\n"
           "        device state <on/off>\n"
           "        device rgb <r> <g> <b> [dimmer]\n"
           "        device temp <temp> [dimmer]\n"
           "        device scene <scene> [dimmer]\n\n"
           "        list devices\n"
           "        list scenes\n")
    sys.exit(1)

if __name__ == "__main__":
    if sys.argv[1] == "list":
        if sys.argv[2] == "devices":
            list_devices()
            sys.exit(0)
        elif sys.argv[2] == "scenes":
            list_scenes()
            sys.exit(0)
        else:
            print_help()

    elif sys.argv[2] == "state":
        if len(sys.argv) < 4:
            print_help()
        if sys.argv[1] not in ip_addresses:
            print_help()
        if sys.argv[3] not in ["on", "off"]:
            print_help()
        if sys.argv[3] == "on":
            set_light_state(ip_addresses[sys.argv[1]], True)
        elif sys.argv[3] == "off":
            set_light_state(ip_addresses[sys.argv[1]], False)
        else:
            print_help()

    elif sys.argv[2] == "rgb":
        if sys.argv[1] not in ip_addresses:
            print_help()
        if len(sys.argv) < 6:
            print_help()
        dimmer = 100 if len(sys.argv) == 6 else int(sys.argv[6])
        set_light_rgb(ip_addresses[sys.argv[1]], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), dimmer)

    elif sys.argv[2] == "temp":
        if sys.argv[1] not in ip_addresses:
            print_help()
        dimmer = 100 if len(sys.argv) == 4 else int(sys.argv[4])
        set_light_temp(ip_addresses[sys.argv[1]], int(sys.argv[3]), dimmer)

    elif sys.argv[2] == "scene":
        if sys.argv[3] not in scenes:
            print_help()
        dimmer = 100 if len(sys.argv) == 4 else int(sys.argv[4])
        set_light_scene(ip_addresses[sys.argv[1]], scenes[sys.argv[3]], dimmer)