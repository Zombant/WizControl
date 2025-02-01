import pystray
from PIL import Image, ImageDraw
import threading

import wiz_control
from wiz_control import ip_addresses, scenes, lighting_groups

def set_state(devices_list, state):
    for device in devices_list:
        wiz_control.set_light_state(ip_addresses[device], state)

# Function to create the system tray icon
def create_image(height, width, color1, color2):
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)   
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)
    return image

# Helper function to create a menu item for a lighting group (Can't pass by value in lambda)
def create_group_menu_item(group):
    return pystray.MenuItem(group, pystray.Menu(
        pystray.MenuItem(f"{group} On", lambda: set_state(lighting_groups[group], True)),
        pystray.MenuItem(f"{group} Off", lambda: set_state(lighting_groups[group], False))
    ))

# Helper function to create a menu item for a device (Can't pass by value in lambda)
def create_device_menu_item(device):
    return pystray.MenuItem(device, pystray.Menu(
        pystray.MenuItem(f"{device} On", lambda: set_state([device], True)),
        pystray.MenuItem(f"{device} Off", lambda: set_state([device], False))
    ))

# Function to setup the system tray icon
def setup_tray():
    icon = pystray.Icon("WiZControl")
    icon.title = "WiZ Control"
    icon.icon = create_image(64, 64, 'black', 'white')

    menu_items = []

    # Create a submenu for each device
    for name, _ in ip_addresses.items():
        menu_items.append(create_device_menu_item(name))

    menu_items.append(pystray.Menu.SEPARATOR)
    
    # Create a submenu for each lighting group
    for group in lighting_groups:
        menu_items.append(create_group_menu_item(group))

    menu_items.append(pystray.Menu.SEPARATOR)

    menu_items.append(pystray.MenuItem('Quit', lambda: icon.stop()))
    
    icon.menu = pystray.Menu(*menu_items)
    icon.run()
    

# Run the system tray icon in a separate thread
if __name__ == "__main__":
    tray_thread = threading.Thread(target=setup_tray)
    tray_thread.start()
