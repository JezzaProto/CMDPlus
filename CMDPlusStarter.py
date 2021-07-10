from os import system, name
import sys

def windows():
	import os, sys, ctypes, shutil, subprocess, json, pathlib
	from time import sleep
	from datetime import datetime
	from winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_CURRENT_USER
	import CMDPlusNGUI as CMDPNGUI
	import CMDPlusGUI as CMDPGUI

	Version = "2.1"

	global FileLoc
	FileLoc = os.getcwd()

	print(f"Preparing CMDPlus V{Version}")

	try:
		Key = r"Software\Policies\Microsoft\Windows\System"
		Reg = ConnectRegistry(None, HKEY_CURRENT_USER)
		CMDDisableKey = OpenKey(Reg, Key)
		CMDDisableVal = QueryValueEx(CMDDisableKey, "DisableCMD")[0]
		if CMDDisableVal == 1:
			print("CMD and scripts are disabled. CMDPlus requires at least batch scripts to be enabled.")
			sleep(5)
			sys.exit(1)
	except FileNotFoundError:
		pass

	try:
		with open("settings.json", "r") as file:
			Settings = json.load(file)
		SettingsFile = True
	except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
		print(f"An error has occured.\nError: {e}\nPresuming no GUI.")
		SettingsFile = False

	if SettingsFile:
		try:
			if Settings["GUI"]:
				try:
					import PySimpleGUI as sg
					GUI = True
				except ImportError:
					GUI = False
			else:
				GUI = False
		except KeyError:
			GUI = False

	if not GUI:
		Settings = CMDPNGUI.main()
	else:
		Settings = CMDPGUI.main()

	print("Saving changed aliases, settings etc.")
	os.chdir(FileLoc)
	tmp = {}
	tmp["tqdm"] = Settings["tqdm"]
	tmp["aliases"] = Settings["aliases"]
	tmp["GUI"] = Settings["GUI"]
	with open("settings.json", "w") as File:
		json.dump(tmp, File, indent=4, sort_keys=True)
	print("Settings saved. Quitting.")
	sleep(2)

def linux():
	import os, sys, ctypes, shutil, subprocess, json, pathlib
	from os import system, name
	from time import sleep
	from datetime import datetime
	import CMDPlusNGUI as CMDPNGUI
	import CMDPlusGUI as CMDPGUI

	Version = "2.1"

	global FileLoc
	FileLoc = os.getcwd()

	print(f"Preparing CMDPlus V{Version}")

	try:
		with open("settings.json", "r") as file:
			Settings = json.load(file)
		SettingsFile = True
	except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
		print(f"An error has occured.\nError: {e}\nPresuming no GUI.")
		SettingsFile = False

	if SettingsFile:
		try:
			if Settings["GUI"]:
				try:
					import PySimpleGUI as sg
					GUI = True
				except ImportError:
					print("PySimpleGUI was not found to be installed\nThis could be because linux's python doesn't come natively with tkinter.\nYou can run\"sudo apt install python3-tk\" and \"pip install -U pysimplegui\" to install both of them.")
					GUI = False
			else:
				GUI = False
		except KeyError:
			GUI = False

	if not GUI:
		Settings = CMDPNGUI.mainlinux()
	else:
		Settings = CMDPGUI.mainlinux()

	print("Saving changed aliases, settings etc.")
	os.chdir(FileLoc)
	tmp = {}
	tmp["tqdm"] = Settings["tqdm"]
	tmp["aliases"] = Settings["aliases"]
	tmp["GUI"] = Settings["GUI"]
	with open("settings.json", "w") as File:
		json.dump(tmp, File, indent=4, sort_keys=True)
	print("Settings saved. Quitting.")
	sleep(2)

if name == "nt":
	windows()
elif name == 'posix':
	linux()
else:
	print('Unknown os, exiting')
	sys.exit()