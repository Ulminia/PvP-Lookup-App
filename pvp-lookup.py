import os
import sys
import requests
import pystray
from PIL import Image
import wx

def upload_file(file_path):
    print(f"Uploading {file_path}")
    # Here you can add the logic to upload the file
    url = "https://pvp-lookup.com/upload/"
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        print("File uploaded successfully.")
        show_tray_message("Upload Successful", f"Successfully uploaded {os.path.basename(file_path)}")
    else:
        print("Failed to upload file.")
        show_tray_message("Upload Failed", "Failed to upload the file.")

def on_quit_callback(icon, item):
    print("Quit item clicked")
    icon.stop()
    wx.CallAfter(wx.GetApp().ExitMainLoop)

def show_tray_message(title, message):
    print(f"{title}: {message}")

def show_info_window():
    frame = InfoFrame()
    frame.Show(True)

def show_manual_upload_dialog():
    dialog = ManualUploadDialog(None)
    dialog.ShowModal()
    dialog.Destroy()

class ManualUploadDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Manual Upload")
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Add a list box to display files
        self.file_listbox = wx.ListBox(self, choices=[], style=wx.LB_SINGLE)
        vbox.Add(self.file_listbox, 1, wx.EXPAND | wx.ALL, 10)

        # Add a button to upload the selected file
        upload_button = wx.Button(self, label="Upload Selected File")
        upload_button.Bind(wx.EVT_BUTTON, self.on_upload)
        vbox.Add(upload_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        # Populate the list box with files
        self.populate_file_list()

        self.SetSizer(vbox)
        self.Fit()

    def populate_file_list(self):
        directory = "C:\\Program Files (x86)\\World of Warcraft\\_retail_\\Logs"
        files = [f for f in os.listdir(directory) if f.startswith("WoWCombatLog-") and f.endswith(".txt")]
        self.file_listbox.Set(files)

    def on_upload(self, event):
        selection = self.file_listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            file_name = self.file_listbox.GetString(selection)
            file_path = os.path.join("C:\\Program Files (x86)\\World of Warcraft\\_retail_\\Logs", file_name)
            upload_file(file_path)
        else:
            wx.MessageBox("Please select a file to upload.", "No file selected", wx.OK | wx.ICON_INFORMATION)

class InfoFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="PvP Lookup Log Uploader", size=(400, 200))
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(panel, label="This application monitors the World of Warcraft logs directory for new log files and uploads them to the server when detected.")
        vbox.Add(label, 0, wx.ALL | wx.EXPAND, 10)
        close_button = wx.Button(panel, label="Close")
        close_button.Bind(wx.EVT_BUTTON, self.on_close)
        vbox.Add(close_button, 0, wx.ALL | wx.CENTER, 10)
        panel.SetSizer(vbox)
    
    def on_close(self, event):
        self.Hide()

class MyApp(wx.App):
    def OnInit(self):
        # You can initialize file monitoring here if needed
        return True

def main():
    # Get the path to the directory containing the executable or the script file
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        exe_dir = sys._MEIPASS
    else:
        # Running as script
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    # Create a tray icon
    icon_path = os.path.join(exe_dir, "icon2.ico")
    icon = pystray.Icon("PvP Lookup Combat Log Uploader")
    icon.icon = Image.open(icon_path)
    icon.title = "PvP Lookup Combat Log Uploader"

    # Add menu items to the tray icon
    quit_item = pystray.MenuItem("Quit", on_quit_callback)
    info_item = pystray.MenuItem("Info", show_info_window)
    manual_upload_item = pystray.MenuItem("Manual Upload", show_manual_upload_dialog)
    icon.menu = (info_item, manual_upload_item, quit_item)

    app = MyApp(False)
    icon.run()

if __name__ == "__main__":
    main()
