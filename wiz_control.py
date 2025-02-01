#!/usr/bin/env python3

import socket
import json
from time import sleep
import sys
import os
import argparse

retry_count = 5

# Path to the settings.json file
script_dir = os.path.dirname(os.path.abspath(__file__))
settings_path = os.path.join(script_dir, "settings.json")

# Import IP addresses from json file
with open(settings_path, "r") as f:
    data = json.load(f)
    devices = data["devices"]
    lighting_groups = data["lighting_groups"]

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

# TODO: Create/modify/delete lighting groups
# TODO: Create/modify/delete devices

def send_command(message, ip, port=38899, retries=retry_count):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    
    for attempt in range(retries):
        try:
            sock.sendto(json.dumps(message).encode(), (ip, port))
            response, addr = sock.recvfrom(1024)
            return json.loads(response.decode())
        except socket.timeout:
            print(f"Timeout occurred, retrying... ({attempt + 1}/{retries})", file=sys.stderr)
        except Exception as e:
            print(f"Error sending command: {e}", file=sys.stderr)
            return 1

    sock.close()
    print(f"Failed to send command after {retries} attempts", file=sys.stderr)
    return 2
        

def set_light_state(ip, state):
    message = {
        "method": "setState",
        "params": {"state": state}
    }

    return send_command(message, ip)
    

def set_light_rgb(ip, r, g, b, dimming=100):
    message = {
        "method": "setPilot",
        "params": { "r": r,
                    "g": g,
                    "b": b,
                    "dimming": dimming}
    }
    
    return send_command(message, ip)

def set_light_temp(ip, temp, dimming=100):
    message = {
        "method": "setPilot",
        "params": { "temp": temp,
                    "dimming": dimming}
    }
    
    return send_command(message, ip)

def set_light_scene(ip, scene_id, dimming=100):
    message = {
        "method": "setPilot",
        "params": { "sceneId": scene_id,
                    "dimming": dimming}
    }

    return send_command(message, ip)

def set_light_dimming(ip, dimming):
    message = {
        "method": "setPilot",
        "params": { "dimming": dimming }
    }

    return send_command(message, ip)

def get_light_status(ip):
    message = {
        "method": "getPilot",
        "params": { }
    }

    return send_command(message, ip)

def list_devices():
    for name, _ in devices.items():
        print(name)

def list_scenes():
    for name, _ in scenes.items():
        print(name)

def list_groups():
    for name, _ in lighting_groups.items():
        print(name)

# TODO: List groups

def print_help(parser):
    parser.print_help()
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control Wiz lights")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List devices or scenes")
    list_parser.add_argument("type", choices=["devices", "scenes", "groups"], help="Type to list")

    device_parser = subparsers.add_parser("control", help="Control a device")
    device_parser.add_argument("name", help="Device name")
    device_parser.add_argument("action", choices=["state", "dimmer", "rgb", "temp", "scene", "status"], help="Action to perform")
    device_parser.add_argument("params", nargs="*", help="Parameters for the action")

    args = parser.parse_args()

    if args.command == "list":
        if args.type == "devices":
            list_devices()
        elif args.type == "scenes":
            list_scenes()
        elif args.type == "groups":
            list_groups()
        else:
            print_help(parser)

    elif args.command == "control":
        if args.name not in devices:
            print_help(parser)

        if args.action == "state":
            if len(args.params) != 1 or args.params[0] not in ["on", "off"]:
                print_help(parser)
            state = args.params[0] == "on"
            set_light_state(devices[args.name]['ip'], state)

        elif args.action == "dimmer":
            if len(args.params) != 1:
                print_help(parser)
            set_light_dimming(devices[args.name]['ip'], int(args.params[0]))

        elif args.action == "rgb":
            if len(args.params) < 3 or len(args.params) > 4:
                print_help(parser)
            r, g, b = map(int, args.params[:3])
            dimming = int(args.params[3]) if len(args.params) == 4 else 100
            set_light_rgb(devices[args.name]['ip'], r, g, b, dimming)

        elif args.action == "temp":
            if len(args.params) < 1 or len(args.params) > 2:
                print_help(parser)
            temp = int(args.params[0])
            dimming = int(args.params[1]) if len(args.params) == 2 else 100
            set_light_temp(devices[args.name]['ip'], temp, dimming)

        elif args.action == "scene":
            if len(args.params) < 1 or len(args.params) > 2 or args.params[0] not in scenes:
                print_help(parser)
            scene_id = scenes[args.params[0]]
            dimming = int(args.params[1]) if len(args.params) == 2 else 100
            set_light_scene(devices[args.name]['ip'], scene_id, dimming)

        elif args.action == "status":
            status = get_light_status(devices[args.name]['ip'])
            print(json.dumps(status, indent=4))

        else:
            print_help(parser)

    else:
        print_help(parser)
