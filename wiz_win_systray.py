import pystray
from PIL import Image, ImageDraw
import threading

import wiz_control
from wiz_control import devices, scenes, lighting_groups

def set_state(devices_list, state):
    for device in devices_list:
        wiz_control.set_light_state(devices[device]['ip'], state)

def set_scene(devices_list, scene_id):
    for device in devices_list:
        wiz_control.set_light_scene(devices[device]['ip'], scene_id)

# Load light bulb image for the system tray icon
def create_light_bulb_image(height, width):
    image = Image.open("light_bulb.png")
    #image = image.resize((width, height))
    return image

# Helper function to create a menu item for a scene for a group
def create_group_scene_menu_item(group, scene):
    return pystray.MenuItem(scene, lambda: set_scene(lighting_groups[group], scenes[scene]))

# Helper function to create a menu item for a scene for a device
def create_device_scene_menu_item(device, scene):
    if devices[device]['type'] == 'light':
        return pystray.MenuItem(scene, lambda: set_scene([device], scenes[scene])) 

# Helper function to create a menu item for a lighting group
def create_group_menu_item(group):
    return pystray.MenuItem(group, pystray.Menu(
        pystray.MenuItem(f"{group} On", lambda: set_state(lighting_groups[group], True)),
        pystray.MenuItem(f"{group} Off", lambda: set_state(lighting_groups[group], False)),
        pystray.MenuItem(f"{group} Scene", pystray.Menu(
            *[create_group_scene_menu_item(group, scene) for scene in scenes]
        ))
    ))

# Helper function to create a menu item for a device
def create_device_menu_item(device):
    menu = []
    menu.append(pystray.MenuItem(f"{device} On", lambda: set_state([device], True)))
    menu.append(pystray.MenuItem(f"{device} Off", lambda: set_state([device], False)))
    if devices[device]['type'] == 'light':
        menu.append(pystray.MenuItem(f"{device} Scene", pystray.Menu(
            *[create_device_scene_menu_item(device, scene) for scene in scenes]
        )))
    return pystray.MenuItem(device, pystray.Menu(*menu))

# Function to setup the system tray icon
def setup_tray():
    icon = pystray.Icon("WiZControl")
    icon.title = "WiZ Control"
    icon.icon = create_light_bulb_image(64, 64)

    menu_items = []

    # Create a submenu for each device
    [menu_items.append(create_device_menu_item(device)) for device in devices]

    menu_items.append(pystray.Menu.SEPARATOR)
    
    # Create a submenu for each lighting group
    [menu_items.append(create_group_menu_item(group)) for group in lighting_groups]

    menu_items.append(pystray.Menu.SEPARATOR)

    menu_items.append(pystray.MenuItem('Quit', lambda: icon.stop()))
    
    icon.menu = pystray.Menu(*menu_items)
    icon.run()
    

# Run the system tray icon in a separate thread
if __name__ == "__main__":
    tray_thread = threading.Thread(target=setup_tray)
    tray_thread.start()
