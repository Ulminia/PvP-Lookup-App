import wx
import os
import sys
import pystray
from PIL import Image
import requests
import datetime

if getattr(sys, 'frozen', False):
	# Running as compiled executable
	exe_dir = sys._MEIPASS
else:
	# Running as script
	exe_dir = os.path.dirname(os.path.abspath(__file__))

# Create a tray icon
icon_path = os.path.join(exe_dir, "icon2.ico")

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

def show_info_window(icon):
	frame = InfoFrame(icon)
	frame.Show(True)

def show_manual_upload_dialog():
	dialog = ManualUploadDialog(None)
	dialog.ShowModal()
	#dialog.Destroy()

class ManualUploadDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="Manual Upload", size=(500, 300))
		self.__close_callback = self.OnClose
		self.icon = Image.open(icon_path)
		self.icon_path = icon_path
		self.SetIcon(wx.Icon(self.icon_path, wx.BITMAP_TYPE_ICO))
		vbox = wx.BoxSizer(wx.VERTICAL)
		self.file_listctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.file_listctrl.InsertColumn(0, "File Name")
		self.file_listctrl.InsertColumn(1, "Date Created")
		# Set the width of the columns
		self.file_listctrl.SetColumnWidth(0, 300)  # Adjust width of first column
		self.file_listctrl.SetColumnWidth(1, 150)  # Adjust width of second column

		vbox.Add(self.file_listctrl, 1, wx.EXPAND | wx.ALL, 10)
		upload_button = wx.Button(self, label="Upload Selected File")
		upload_button.Bind(wx.EVT_BUTTON, self.on_upload)
		vbox.Add(upload_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
		close_button = wx.Button(self, label="Close")
		close_button.Bind(wx.EVT_BUTTON, self.on_close)  # Bind close button to on_close event handler
		vbox.Add(close_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
		self.populate_file_list()
		self.SetSizer(vbox)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)

	def OnClose(self, event):
		print ('In OnClose')
		event.Skip()

	def OnDestroy(self, event):
		print ('In OnDestroy')
		event.Skip()

	def _close(self):
		print ('In _close')
		self.Hide()
		self.Destroy()
	def on_close(self, event):
		print ('In On_Close')
		self.Hide()  # Hide the dialog when close button is clicked
		#self.Destroy()

	# Override the Close method to handle the closing event
	def Close(self, *args, **kwargs):
		#self.Hide()  # Hide the dialog when close method is called
		print ('In Close')
		self.Destroy()

	def populate_file_list(self):
		directory = "C:\\Program Files (x86)\\World of Warcraft\\_retail_\\Logs"
		files = [f for f in os.listdir(directory) if f.startswith("WoWCombatLog-") and f.endswith(".txt")]
		for file_name in files:
			file_path = os.path.join(directory, file_name)
			created_time = os.path.getctime(file_path)
			created_date = datetime.datetime.fromtimestamp(created_time).strftime("%Y-%m-%d %H:%M:%S")
			index = self.file_listctrl.InsertItem(self.file_listctrl.GetItemCount(), file_name)
			self.file_listctrl.SetItem(index, 1, created_date)

	def on_upload(self, event):
		selection = self.file_listctrl.GetFirstSelected()
		if selection != wx.NOT_FOUND:
			file_name = self.file_listctrl.GetItemText(selection)
			file_path = os.path.join("C:\\Program Files (x86)\\World of Warcraft\\_retail_\\Logs", file_name)
			upload_file(file_path)
		else:
			wx.MessageBox("Please select a file to upload.", "No file selected", wx.OK | wx.ICON_INFORMATION)


class InfoFrame(wx.Frame):
	def __init__(self, icon):
		super().__init__(None, title="PvP Lookup Log Uploader", size=(400, 200))
		self.icon = icon
		self.icon_path = icon_path  # Assuming 'exe_dir' is defined in the main part of your script
		self.SetIcon(wx.Icon(self.icon_path, wx.BITMAP_TYPE_ICO))  # Set the frame icon
		panel = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)
		label = wx.StaticText(panel, label="This application monitors the World of Warcraft logs directory for new log files and uploads them to the server when detected. GitHub repo can be seen here https://github.com/Ulminia/PvP-Lookup-App", style=wx.ST_ELLIPSIZE_MIDDLE)
		label.Wrap(380)  # Set the width to wrap at (adjust as needed)
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