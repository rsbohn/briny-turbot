#boot.py for Feather M0
#disable HID to free up some needed memory
import usb_hid
usb_hid.disable()
print("HID Disabled.")
