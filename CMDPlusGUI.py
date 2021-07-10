def main():
	import os, sys, ctypes, shutil, subprocess, json, pathlib
	from os import system, name
	from time import sleep
	from datetime import datetime
	from winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_CURRENT_USER
	import PySimpleGUI as sg

	def clear():
		window.FindElement('-OUTPUT-').Update('')

	def rootPath():
		path = sys.executable
		while os.path.split(path)[1]:
			path = os.path.split(path)[0]
		return path

	def checkIdle():
		if "idlelib.run" in sys.modules:
			return True
		return False

	def error(msg):
		cprint(msg, colors="red on black")

	def info(msg):
		cprint(msg, colors="orange on black")

	def success(msg):
		cprint(msg, colors="green on black")

	Version = "2.0"

	print(f"Setting up CMDPlusGUI V{Version}")

	# Colours
	DARK_BLUE = 0x01
	DARK_GREEN = 0x02
	BLUE = 0x03
	RED = 0x04
	DARK_PURPLE = 0x05
	GOLD = 0x06
	WHITE = 0x07
	GREY = 0x08
	DARK_BLUE = 0x09
	GREEN = 0x0a
	LIGHT_BLUE = 0x0b
	LIGHT_RED = 0x0c
	PURPLE = 0x0d
	YELLOW = 0x0e

	

	if name != "nt":
		print("Non-windows systems are not yet supported.")
		sleep(5)
		sys.exit(1)

	Yes = ["Y", "YES"]
	All = ["*.*", "all"]

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
		print("Settings file found.")
	except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
		print(f"An error has occured.\nError: {e}\nRunning without aliases")
		SettingsFile = False

	if SettingsFile:
		try:
			if Settings["tqdm"]:
				try:
					from tqdm import tqdm
					TQDMInstall = True
				except ImportError:
					TQDMInstall = False
			else:
				TQDMInstall = False
		except KeyError:
			TQDMInstall = False

	global FileLoc
	FileLoc = os.getcwd()

	os.chdir(rootPath())

	print("Setup finished.\nEnter \"exit\" to quit.")

	layout = [	[sg.Text("CMDPlus")],
				[sg.Multiline(size=(100,25), key="-OUTPUT-", background_color="black", text_color="white", reroute_stdout=True, reroute_stderr=True, write_only=True, disabled=True, autoscroll=True)],
				[sg.In(size=(100,1),key="-INPUT-")],
				[sg.Button(button_text="Enter", bind_return_key=True), sg.Button(button_text="Clear"), sg.Button(button_text="Exit")]]
	
	sg.theme("Black")
	window = sg.Window(f"CMDPlus V{Version}", layout, finalize=True)

	cprint = sg.cprint
	sg.cprint_set_output_destination(window, "-OUTPUT-")

	while True:
		cprint("CMDPlus: ", colors="green on black", end="")
		cprint(f"{os.getcwd()}> ", colors="white on black", end="")
		event, values = window.read()
		if event in (sg.WIN_CLOSED, "Exit"):
			cprint("Closing CMDPlus.", colors="green on black")
			break
		if event == "Clear":
			clear()
		if event == "Enter":
			window.find_element("-INPUT-").update("")
			UserInput = values["-INPUT-"]
			print(UserInput)
			Command = UserInput.split(" ")[0].lower()
			if len(Command) == 0:
					continue
			try:
				Args = UserInput.split(" ")[1:]
			except:
				pass
			if SettingsFile:
				try:
					Command = Settings["aliases"][Command]
				except KeyError:
					pass
			try:
				if Command[1] == ":" and Command[0].isalpha():
					os.chdir(Command)
					os.chdir("\\")
					success(f"Changed directory to {os.getcwd()}")
					continue
			except:
				pass
			if Command == "explorer":
				if len(Args) == 0:
					info(f"Opening explorer in {os.getcwd()}")
					system(f'explorer %cd%')
					continue
				Dir = "\\".join(Args)
				info(f"Opening explorer in {Dir}")
				system(f'start "{os.path.realpath(Dir)}"')
				continue
			elif Command == "cd":
				if len(Args) == 0:
					info(f"Current Directory: {os.getcwd()}")
					continue
				cdArgs = " ".join(Args)
				try:
					os.chdir(cdArgs)
					success(f"Changed directory to {os.getcwd()}")
					continue
				except (FileNotFoundError, PermissionError) as e:
					error(f"Error changing directory.\nError: {e}")
					continue
			elif Command == "cls":
				clear()
				continue
			elif Command == "exit":
				break
			elif Command == "title":
				ctypes.windll.kernel32.SetConsoleTitleW(" ".join(Args))
				window.TKroot.title(" ".join(Args))
				continue
			elif Command == "del":
				if len(Args) == 0:
					error("Deletion command missing arguments.")
					continue
				if Args[0].lower() in All:
					info("Are you sure you want to delete this directories contents? Y/N")
					confirm = input()
					if confirm.upper() in Yes:
						if TQDMInstall:
							for dirpath, _, filenames in tqdm(os.walk(os.getcwd(), topdown=False), ascii=True, desc="Deletion Progress"):
								try:
									os.rmdir(dirpath)
								except OSError as ex:
									error(f"Error deleting {dirpath}:\n{ex}")
							continue
						else:
							for dirpath, _, filenames in os.walk(os.getcwd(), topdown=False):
								for file in filenames:
									try:
										os.remove(file)
									except OSError as ex:
										error(f"Error deleting {file}:\n{ex}")
								try:
									os.rmdir(dirpath)
								except OSError as ex:
									error(f"Error deleting {file}:\n{ex}")
							continue
					continue
				else:
					if not os.access(" ".join(Args), os.F_OK):
						error("This file does not exist.")
						continue
					if not os.access(" ".join(Args), os.W_OK):
						error("You do not have permissions to delete this file.")
						continue
					info(f"Are you sure you want to delete {' '.join(Args)}? Y/N")
					confirm = input()
					if confirm.upper() in Yes:
						try:
							if os.path.isdir(" ".join(Args)):
								os.rmdir(" ".join(Args))
							else:
								os.remove(" ".join(Args))
							success("{' '.join(Args)} deleted.")
						except (IsADirectoryError, OSError, WindowsError) as e:
							error(f"Could not remove file.\nError: {e}")
							continue
					continue
			elif Command == "dir":
				DirArgs = " ".join(Args)
				output = os.popen(f"dir /a {DirArgs}").read()
				print(output)
				continue
			elif Command == "aliases":
				if len(Args) == 0:
					print("{:<15} | {:<15}".format("Command","Alias"))
					print("=-=-=-=-=-=-=-=-|-=-=-=-=-=-=")
					for Key, Item in Settings["aliases"].items():
						print("{:<15} | {:<15}".format(Key, Item))
					continue
				if Args[0].lower() == "add":
					try:
						Command = Args[1]
						Alias = Args[2]
					except IndexError:
						error("Missing arguments.")
						continue
					try:
						OldCommand = Settings["aliases"][Command]
						if OldCommand == Alias:
							error("This command is already aliased to this alias.")
							continue
						Confirm = input(f"This command is already aliased to {OldCommand}.\nDo you want to overwrite it?\n")
						if Confirm.upper() in Yes:
							Settings["aliases"][Command] = Alias
							success(f"\"{Command}\" alias updated to \"{Alias}\".")
							continue
						else:
							info("Not continuing.")
							continue
					except (IndexError, KeyError):
						Settings["aliases"][Command] = Alias
						info(f"\"{Command}\" alias set to \"{Alias}\".")
						continue
				elif Args[0].lower() == "remove":
					try:
						Command = Args[1]
					except IndexError:
						error("Missing arguments.")
						continue
					try:
						OldCommand = Settings["aliases"][Command]
						Confirm = input(f"This command is aliased to {OldCommand}.\nDo you want to remove it?\n")
						if Confirm.upper() in Yes:
							del Settings["aliases"][Command]
							success(f"{Command} alias removed.")
							continue
						else:
							info("Not continuing.")
							continue
					except KeyError:
						error("This is not an alias.")
						continue
				elif Args[0].lower() == "view":
					try:
						Command = Args[1]
					except IndexError:
						print("{:<15} | {:<15}".format("Command","Alias"))
						print("=-=-=-=-=-=-=-=-|-=-=-=-=-=-=")
						for Key, Item in Settings["aliases"].items():
							print("{:<15} | {:<15}".format(Key, Item))
						continue
					try:
						OldCommand = Settings["aliases"][Command]
						success(f"\"{Command}\" is aliased to \"{OldCommand}\"")
						continue
					except KeyError:
						error(f"\"{Command}\" is not aliased.")
						continue
			elif Command == "reload":
				OldDir = os.getcwd()
				os.chdir(FileLoc)
				try:
					with open("settings.json", "r") as file:
						Settings = json.load(file)
					SettingsFile = True
					success("Settings file reloaded.")
				except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
					error(f"An error has occured.\nError: {e}\nRunning without aliases")
					SettingsFile = False
					continue
				if SettingsFile:
					try:
						if Settings["tqdm"]:
							try:
								from tqdm import tqdm
								TQDMInstall = True
							except ImportError:
								TQDMInstall = False
						else:
							TQDMInstall = False
					except KeyError:
						TQDMInstall = False
				os.chdir(OldDir)
				info("Finished reloading.")
				continue
			elif Command == "more":
				if len(Args) == 0:
					error("No file entered.")
					continue
				Filename = " ".join(Args)
				try:
					with open(Filename, mode="r", encoding="utf-8") as File:
						info(f"Contents of {Filename}:")
						Contents = File.read()
						print(Contents)
						File.close()
					success("End of file.")
				except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
					error(f"An error has occured.\nError: {e}")
				continue
			elif Command == "settings":
				if len(Args) == 0:
					info("Current Settings:")
					cprint(f"TQDM Installed: {Settings['tqdm']}", colors="blue on black")
					cprint(f"GUI Enabled: {Settings['GUI']}", colors="blue on black")
					success(f"End of settings.")
					continue
				if Args[0].upper() == "TOGGLE":
					try:
						if Args[1].upper() == "TQDM":
							cprint(f"TQDM Installed: {Settings['tqdm']}", colors="blue on black")
							confirm = input("Do you want to toggle TQDM settings? (Y/N):\n")
							if confirm.upper() in Yes:
								Settings["tqdm"] = not Settings["tqdm"]
								info(f"Changed TQDM settings to: {Settings['tqdm']}")
							else:
								info("Not changing.")
							continue
						if Args[1].upper() == "GUI":
							cprint(f"GUI Installed: {Settings['GUI']}", colors="blue on black")
							confirm = input("Do you want to toggle GUI settings? (Y/N):\n")
							if confirm.upper() in Yes:
								Settings["GUI"] = not Settings["GUI"]
								info(f"Changed GUI settings to: {Settings['GUI']}\nRestart CMDPlus to save changes.")
							else:
								info("Not changing.")
							continue
					except IndexError:
						error("No setting to toggle entered.")
			elif Command == "mkdir":
				if len(Args) == 0:
					error("No directory name entered.")
					continue
				DirName = " ".join(Args)
				if os.path.exists(DirName):
					error("This directory already exists.")
					continue
				try:
					os.mkdir(DirName)
					success(f"{DirName} directory created.")
					continue
				except NotADirectoryError as e:
					error(f"An error has occured.\nError: {e}")
					continue
			elif Command == "rmdir":
				if len(Args) == 0:
					error("No directory name entered.")
					continue
				DirName = " ".join(Args)
				if not os.path.exists(DirName):
					error("This directory doesnt exist.")
					continue
				confirm = input(f"Are you sure you want to remove {DirName}?\n").upper()
				if confirm not in Yes:
					error("Deletion cancelled.")
					continue
				try:
					os.rmdir(DirName)
					success(f"{DirName} directory removed.")
					continue
				except OSError as e:
					error(f"An error has occured.\nError: {e}")
					continue
			elif Command == "cmd":
				subprocess.Popen(["cmd"])
				continue
			else:
				try:
					output = os.popen(UserInput).read()
					if output == "":
						print("No output.")
					else:
						print(output)
				except KeyboardInterrupt:
					error("Keyboard interrupt.\nCommand cancelled.")
					continue
	return Settings

def mainlinux():
	import os, sys, shutil, subprocess, json, pathlib
	from os import system, name
	from time import sleep
	from datetime import datetime
	import PySimpleGUI as sg

	def clear():
		window.FindElement('-OUTPUT-').Update('')

	def rootPath():
		path = sys.executable
		while os.path.split(path)[1]:
			path = os.path.split(path)[0]
		return path

	def checkIdle():
		if "idlelib.run" in sys.modules:
			return True
		return False

	def error(msg):
		cprint(msg, colors="red on black")

	def info(msg):
		cprint(msg, colors="orange on black")

	def success(msg):
		cprint(msg, colors="green on black")

	Version = "2.0"

	print(f"Setting up CMDPlusGUI V{Version}")

	# Colours
	DARK_BLUE = 0x01
	DARK_GREEN = 0x02
	BLUE = 0x03
	RED = 0x04
	DARK_PURPLE = 0x05
	GOLD = 0x06
	WHITE = 0x07
	GREY = 0x08
	DARK_BLUE = 0x09
	GREEN = 0x0a
	LIGHT_BLUE = 0x0b
	LIGHT_RED = 0x0c
	PURPLE = 0x0d
	YELLOW = 0x0e

	
	Yes = ["Y", "YES"]
	All = ["*.*", "all"]

	try:
		with open("settings.json", "r") as file:
			Settings = json.load(file)
		SettingsFile = True
		print("Settings file found.")
	except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
		print(f"An error has occured.\nError: {e}\nRunning without aliases")
		SettingsFile = False

	if SettingsFile:
		try:
			if Settings["tqdm"]:
				try:
					from tqdm import tqdm
					TQDMInstall = True
				except ImportError:
					TQDMInstall = False
			else:
				TQDMInstall = False
		except KeyError:
			TQDMInstall = False

	global FileLoc
	FileLoc = os.getcwd()

	os.chdir(rootPath())

	print("Setup finished.\nEnter \"exit\" to quit.")

	layout = [	[sg.Text("CMDPlus")],
				[sg.Multiline(size=(100,25), key="-OUTPUT-", background_color="black", text_color="white", reroute_stdout=True, reroute_stderr=True, write_only=True, disabled=True, autoscroll=True)],
				[sg.In(size=(100,1),key="-INPUT-")],
				[sg.Button(button_text="Enter", bind_return_key=True), sg.Button(button_text="Clear"), sg.Button(button_text="Exit")]]
	
	sg.theme("Black")
	window = sg.Window(f"CMDPlus V{Version}", layout, finalize=True)

	cprint = sg.cprint
	sg.cprint_set_output_destination(window, "-OUTPUT-")

	while True:
		cprint("CMDPlus: ", colors="green on black", end="")
		cprint(f"{os.getcwd()}> ", colors="white on black", end="")
		event, values = window.read()
		if event in (sg.WIN_CLOSED, "Exit"):
			cprint("Closing CMDPlus.", colors="green on black")
			break
		if event == "Clear":
			clear()
		if event == "Enter":
			window.find_element("-INPUT-").update("")
			UserInput = values["-INPUT-"]
			print(UserInput)
			Command = UserInput.split(" ")[0].lower()
			if len(Command) == 0:
					continue
			try:
				Args = UserInput.split(" ")[1:]
			except:
				pass
			if SettingsFile:
				try:
					Command = Settings["aliases"][Command]
				except KeyError:
					pass
			try:
				if Command[1] == ":" and Command[0].isalpha():
					os.chdir(Command)
					os.chdir("\\")
					success(f"Changed directory to {os.getcwd()}")
					continue
			except:
				pass
			if Command == "explorer":
				if len(Args) == 0:
					info(f"Opening explorer in {os.getcwd()}")
					system(f'explorer %cd%')
					continue
				Dir = "\\".join(Args)
				info(f"Opening explorer in {Dir}")
				system(f'start "{os.path.realpath(Dir)}"')
				continue
			elif Command == "cd":
				if len(Args) == 0:
					info(f"Current Directory: {os.getcwd()}")
					continue
				cdArgs = " ".join(Args)
				try:
					os.chdir(cdArgs)
					success(f"Changed directory to {os.getcwd()}")
					continue
				except (FileNotFoundError, PermissionError) as e:
					error(f"Error changing directory.\nError: {e}")
					continue
			elif Command == "cls":
				clear()
				continue
			elif Command == "exit":
				break
			elif Command == "title":
				window.TKroot.title(" ".join(Args))
				continue
			elif Command == "del":
				if len(Args) == 0:
					error("Deletion command missing arguments.")
					continue
				if Args[0].lower() in All:
					info("Are you sure you want to delete this directories contents? Y/N")
					confirm = input()
					if confirm.upper() in Yes:
						if TQDMInstall:
							for dirpath, _, filenames in tqdm(os.walk(os.getcwd(), topdown=False), ascii=True, desc="Deletion Progress"):
								try:
									os.rmdir(dirpath)
								except OSError as ex:
									error(f"Error deleting {dirpath}:\n{ex}")
							continue
						else:
							for dirpath, _, filenames in os.walk(os.getcwd(), topdown=False):
								for file in filenames:
									try:
										os.remove(file)
									except OSError as ex:
										error(f"Error deleting {file}:\n{ex}")
								try:
									os.rmdir(dirpath)
								except OSError as ex:
									error(f"Error deleting {file}:\n{ex}")
							continue
					continue
				else:
					if not os.access(" ".join(Args), os.F_OK):
						error("This file does not exist.")
						continue
					if not os.access(" ".join(Args), os.W_OK):
						error("You do not have permissions to delete this file.")
						continue
					info(f"Are you sure you want to delete {' '.join(Args)}? Y/N")
					confirm = input()
					if confirm.upper() in Yes:
						try:
							if os.path.isdir(" ".join(Args)):
								os.rmdir(" ".join(Args))
							else:
								os.remove(" ".join(Args))
							success("{' '.join(Args)} deleted.")
						except (IsADirectoryError, OSError, WindowsError) as e:
							error(f"Could not remove file.\nError: {e}")
							continue
					continue
			elif Command == "dir":
				DirArgs = " ".join(Args)
				output = os.popen(f"dir /a {DirArgs}").read()
				print(output)
				continue
			elif Command == "aliases":
				if len(Args) == 0:
					print("{:<15} | {:<15}".format("Command","Alias"))
					print("=-=-=-=-=-=-=-=-|-=-=-=-=-=-=")
					for Key, Item in Settings["aliases"].items():
						print("{:<15} | {:<15}".format(Key, Item))
					continue
				if Args[0].lower() == "add":
					try:
						Command = Args[1]
						Alias = Args[2]
					except IndexError:
						error("Missing arguments.")
						continue
					try:
						OldCommand = Settings["aliases"][Command]
						if OldCommand == Alias:
							error("This command is already aliased to this alias.")
							continue
						Confirm = input(f"This command is already aliased to {OldCommand}.\nDo you want to overwrite it?\n")
						if Confirm.upper() in Yes:
							Settings["aliases"][Command] = Alias
							success(f"\"{Command}\" alias updated to \"{Alias}\".")
							continue
						else:
							info("Not continuing.")
							continue
					except (IndexError, KeyError):
						Settings["aliases"][Command] = Alias
						info(f"\"{Command}\" alias set to \"{Alias}\".")
						continue
				elif Args[0].lower() == "remove":
					try:
						Command = Args[1]
					except IndexError:
						error("Missing arguments.")
						continue
					try:
						OldCommand = Settings["aliases"][Command]
						Confirm = input(f"This command is aliased to {OldCommand}.\nDo you want to remove it?\n")
						if Confirm.upper() in Yes:
							del Settings["aliases"][Command]
							success(f"{Command} alias removed.")
							continue
						else:
							info("Not continuing.")
							continue
					except KeyError:
						error("This is not an alias.")
						continue
				elif Args[0].lower() == "view":
					try:
						Command = Args[1]
					except IndexError:
						print("{:<15} | {:<15}".format("Command","Alias"))
						print("=-=-=-=-=-=-=-=-|-=-=-=-=-=-=")
						for Key, Item in Settings["aliases"].items():
							print("{:<15} | {:<15}".format(Key, Item))
						continue
					try:
						OldCommand = Settings["aliases"][Command]
						success(f"\"{Command}\" is aliased to \"{OldCommand}\"")
						continue
					except KeyError:
						error(f"\"{Command}\" is not aliased.")
						continue
			elif Command == "reload":
				OldDir = os.getcwd()
				os.chdir(FileLoc)
				try:
					with open("settings.json", "r") as file:
						Settings = json.load(file)
					SettingsFile = True
					success("Settings file reloaded.")
				except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
					error(f"An error has occured.\nError: {e}\nRunning without aliases")
					SettingsFile = False
					continue
				if SettingsFile:
					try:
						if Settings["tqdm"]:
							try:
								from tqdm import tqdm
								TQDMInstall = True
							except ImportError:
								TQDMInstall = False
						else:
							TQDMInstall = False
					except KeyError:
						TQDMInstall = False
				os.chdir(OldDir)
				info("Finished reloading.")
				continue
			elif Command == "more":
				if len(Args) == 0:
					error("No file entered.")
					continue
				Filename = " ".join(Args)
				try:
					with open(Filename, mode="r", encoding="utf-8") as File:
						info(f"Contents of {Filename}:")
						Contents = File.read()
						print(Contents)
						File.close()
					success("End of file.")
				except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
					error(f"An error has occured.\nError: {e}")
				continue
			elif Command == "settings":
				if len(Args) == 0:
					info("Current Settings:")
					cprint(f"TQDM Installed: {Settings['tqdm']}", colors="blue on black")
					cprint(f"GUI Enabled: {Settings['GUI']}", colors="blue on black")
					success(f"End of settings.")
					continue
				if Args[0].upper() == "TOGGLE":
					try:
						if Args[1].upper() == "TQDM":
							cprint(f"TQDM Installed: {Settings['tqdm']}", colors="blue on black")
							confirm = input("Do you want to toggle TQDM settings? (Y/N):\n")
							if confirm.upper() in Yes:
								Settings["tqdm"] = not Settings["tqdm"]
								info(f"Changed TQDM settings to: {Settings['tqdm']}")
							else:
								info("Not changing.")
							continue
						if Args[1].upper() == "GUI":
							cprint(f"GUI Installed: {Settings['GUI']}", colors="blue on black")
							confirm = input("Do you want to toggle GUI settings? (Y/N):\n")
							if confirm.upper() in Yes:
								Settings["GUI"] = not Settings["GUI"]
								info(f"Changed GUI settings to: {Settings['GUI']}\nRestart CMDPlus to save changes.")
							else:
								info("Not changing.")
							continue
					except IndexError:
						error("No setting to toggle entered.")
			elif Command == "mkdir":
				if len(Args) == 0:
					error("No directory name entered.")
					continue
				DirName = " ".join(Args)
				if os.path.exists(DirName):
					error("This directory already exists.")
					continue
				try:
					os.mkdir(DirName)
					success(f"{DirName} directory created.")
					continue
				except NotADirectoryError as e:
					error(f"An error has occured.\nError: {e}")
					continue
			elif Command == "rmdir":
				if len(Args) == 0:
					error("No directory name entered.")
					continue
				DirName = " ".join(Args)
				if not os.path.exists(DirName):
					error("This directory doesnt exist.")
					continue
				confirm = input(f"Are you sure you want to remove {DirName}?\n").upper()
				if confirm not in Yes:
					error("Deletion cancelled.")
					continue
				try:
					os.rmdir(DirName)
					success(f"{DirName} directory removed.")
					continue
				except OSError as e:
					error(f"An error has occured.\nError: {e}")
					continue
			elif Command == "cmd":
				subprocess.Popen(["cmd"])
				continue
			else:
				try:
					output = os.popen(UserInput).read()
					if output == "":
						print("No output.")
					else:
						print(output)
				except KeyboardInterrupt:
					error("Keyboard interrupt.\nCommand cancelled.")
					continue
	return Settings
