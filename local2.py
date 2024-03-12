import wx
import sys
import os
import requests
import datetime
from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QAction, QDialog, QLabel, QVBoxLayout, QTableWidget, QListWidget, QTableWidgetItem, QPushButton, QMessageBox, QHeaderView, QAbstractItemView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from plyer import notification
from plyer.utils import platform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


if getattr(sys, 'frozen', False):
	# Running as compiled executable
	exe_dir = sys._MEIPASS
else:
	# Running as script
	exe_dir = os.path.dirname(os.path.abspath(__file__))

# Create a tray icon
icon_path = os.path.join(exe_dir, "icon2.ico")

def show_tray_message(ntitle, nmessage):
	#toaster = ToastNotifier()
	#toaster.show_toast(title, message, duration=5, icon_path = icon_path, threaded=True)
	notification.notify(title=ntitle, message=nmessage, app_name='PvP Lookup', app_icon=icon_path, timeout=10, ticker='', toast=True, hints={})
	
def test_try_msg():
	show_tray_message("Upload Failed", "Failed to upload the file.")

def on_quit_callback(icon, item):
	print("Quit item clicked", flush=True)
	icon.stop()
	wx.CallAfter(wx.GetApp().ExitMainLoop)

def show_info_window():
	dialog = InfoFrame(None)
	dialog.ShowModal()

def show_manual_upload_dialog():
	dialog = ManualUploadDialog(None)
	dialog.ShowModal()
	
# Function to upload file
def upload_file(file_path):
	print(f"Uploading {file_path}")
	# Read the contents of the file
	with open(file_path, 'r', encoding='utf-8') as f:
		file_contents = f.read()
	# URL for the upload endpoint
	url = "http://127.0.0.1:8000/api/upload/"
	# Prepare the payload for the request
	payload = {'file_contents': file_contents}
	# Send the request
	response = requests.post(url, json=payload)
	# Check the response status code
	if response.status_code == 200:
		print("File uploaded successfully.")
		show_tray_message("Upload Successful", f"Successfully uploaded {os.path.basename(file_path)}")
	#elseif response.status_code == 400:
	#	print("File not uploaded.")
	#	show_tray_message("Combat log exists", f"Successfully uploaded {os.path.basename(file_path)}")
	else:
		print("Failed to upload file.")
		show_tray_message("Upload Failed", "Failed to upload the file.")

# Class for handling new log file creation
class NewLogFileHandler(FileSystemEventHandler):
	def on_created(self, event):
		if not event.is_directory and event.src_path.endswith(".txt") and "WoWCombatLog-" in event.src_path:
			print(f"New log file detected: {event.src_path}")
			upload_file(event.src_path)

# Function to setup file monitoring
def setup_file_monitoring():
	path_to_watch = "C:\\Program Files (x86)\\World of Warcraft\\_retail_\\Logs"
	event_handler = NewLogFileHandler()
	observer = Observer()
	observer.schedule(event_handler, path=path_to_watch, recursive=False)
	observer.start()

# Main application class
class App(QApplication):
	def __init__(self, argv):
		super().__init__(argv)
		self.tray_icon = None
		self.setup_tray_icon()
		setup_file_monitoring()

	# Function to setup the system tray icon and menu
	def setup_tray_icon(self):
		self.tray_icon = QSystemTrayIcon(QIcon("icon2.ico"), self)
		self.tray_icon.setToolTip("PvP Lookup Combat Log Uploader")

		# Create a menu for the system tray icon
		menu = QMenu()
		info_action = QAction("Info", self)
		info_action.triggered.connect(self.show_info_window)
		manual_upload_action = QAction("Manual Upload", self)
		manual_upload_action.triggered.connect(self.show_manual_upload_dialog)
		quit_action = QAction("Quit", self)
		quit_action.triggered.connect(self.on_quit)
		menu.addAction(info_action)
		menu.addAction(manual_upload_action)
		menu.addAction(quit_action)

		# Set the menu to the system tray icon
		self.tray_icon.setContextMenu(menu)

		# Show the system tray icon
		self.tray_icon.show()

	# Function to show the info window
	def show_info_window(self):
		dialog = InfoFrame()
		dialog.exec_()

	# Function to show the manual upload dialog
	def show_manual_upload_dialog(self):
		dialog = ManualUploadDialog()
		dialog.exec_()

	# Function to handle quit action
	def on_quit(self):
		print("Quit item clicked")
		self.tray_icon.hide()
		self.quit()

class InfoFrame(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("PvP Lookup Log Uploader")
		self.icon_path = icon_path
		self.setWindowIcon(QIcon(self.icon_path))  # Set window icon
		self.resize(400, 200)

		self.label = QLabel("This application monitors the World of Warcraft logs directory for new log files and uploads them to the server when detected. GitHub repo can be seen here https://github.com/Ulminia/PvP-Lookup-App")
		self.label.setWordWrap(True)

		self.close_button = QPushButton("Close")
		self.close_button.clicked.connect(self.close)

		layout = QVBoxLayout()
		layout.addWidget(self.label)
		layout.addWidget(self.close_button)
		self.setLayout(layout)

	def on_close(self, event):
		self.Hide()

	def closeEvent(self, event):
		event.ignore()  # Ignore the close event
		self.hide()  # Hide the dialog instead of closing it
		
# Class for manual upload dialog
class ManualUploadDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Manual Upload")
		self.icon_path = icon_path
		self.setWindowIcon(QIcon(self.icon_path))  # Set window icon
		self.resize(500, 300)
		self.setup_ui()

	# Function to setup the UI of the dialog
	def setup_ui(self):
		layout = QVBoxLayout(self)
		self.file_table_widget = QTableWidget()
		self.file_table_widget.setColumnCount(2)  # Two columns for file name and created date
		self.file_table_widget.setHorizontalHeaderLabels(["File Name", "Created Date"])
		layout.addWidget(self.file_table_widget)
		self.upload_button = QPushButton("Upload Selected File")
		self.upload_button.clicked.connect(self.on_upload)
		layout.addWidget(self.upload_button)
		self.close_button = QPushButton("Close")
		self.close_button.clicked.connect(self.close)
		layout.addWidget(self.close_button)        
		self.populate_file_list()
		# Adjust column widths
		self.set_column_percentages([40, 20])  # Set column percentages
		self.file_table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # Prevent resizing
		self.file_table_widget.setSelectionMode(QAbstractItemView.SingleSelection)  # Set single selection mode
		self.make_created_date_column_unselectable()


	# Function to populate the file list in the dialog
	def populate_file_list(self):
		directory = "C:\\Program Files (x86)\\World of Warcraft\\_retail_\\Logs"
		files = [f for f in os.listdir(directory) if f.startswith("WoWCombatLog-") and f.endswith(".txt")]
		files.sort(key=lambda x: os.path.getctime(os.path.join(directory, x)))
		for file_name in files:
			file_path = os.path.join(directory, file_name)
			created_time = os.path.getctime(file_path)
			created_date = datetime.datetime.fromtimestamp(created_time).strftime("%Y-%m-%d %H:%M:%S")
			row_position = self.file_table_widget.rowCount()
			self.file_table_widget.insertRow(row_position)
			self.file_table_widget.setItem(row_position, 0, QTableWidgetItem(file_name))
			self.file_table_widget.setItem(row_position, 1, QTableWidgetItem(created_date))

	# Function to handle file upload
	def on_upload(self):
		selected_items = self.file_table_widget.selectedItems()
		if selected_items:
			file_name_item = selected_items[0]  # Get the first selected item (file name)
			file_name = file_name_item.text()
			row_index = file_name_item.row()  # Get the row index of the selected item
			created_date_item = self.file_table_widget.item(row_index, 1)  # Get the corresponding created date item
			created_date = created_date_item.text()
			file_path = os.path.join("C:\\Program Files (x86)\\World of Warcraft\\_retail_\\Logs", file_name)
			print(f"File selected {file_path}!")
			upload_file(file_path)
		else:
			show_tray_message("No file selected", "Please select a file to upload.")
			#QMessageBox.warning(self, "No file selected", "Please select a file to upload.")

	def set_column_percentages(self, percentages):
		total_width = self.file_table_widget.width()
		for column, percentage in enumerate(percentages):
			width = round(total_width * percentage / 100)
			self.file_table_widget.setColumnWidth(column, width)
			
	def make_created_date_column_unselectable(self):
		for row in range(self.file_table_widget.rowCount()):
			item = self.file_table_widget.item(row, 1)
			item.setFlags(item.flags() & ~Qt.ItemIsSelectable)  # Remove selectable flag
			
	def closeEvent(self, event):
		event.ignore()  # Ignore the close event
		self.hide()  # Hide the dialog instead of closing it

if __name__ == "__main__":
	app = App(sys.argv)
	sys.exit(app.exec_())
