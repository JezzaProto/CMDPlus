import os, sys, ctypes, shutil, subprocess, json, pathlib
from os import system, name
from time import sleep
from datetime import datetime
from winreg import ConnectRegistry, OpenKey, QueryValueEx, HKEY_CURRENT_USER

def clear():
    if checkIdle():
        print("\n"*100)
    elif name == "nt":
        _ = system("cls")
    else:
        _ = system("clear")

def rootPath():
    path = sys.executable
    while os.path.split(path)[1]:
        path = os.path.split(path)[0]
    return path

def checkIdle():
    if "idlelib.run" in sys.modules:
        return True
    return False

def setColour(colour):
    if checkIdle():
        return False
    handle = ctypes.windll.kernel32.GetStdHandle(-11)
    return ctypes.windll.kernel32.SetConsoleTextAttribute(handle, colour)

def error(msg):
    if checkIdle():
        print(msg)
    else:
        setColour(RED)
        print(msg)
        setColour(WHITE)

def info(msg):
    if checkIdle():
        print(msg)
    else:
        setColour(GOLD)
        print(msg)
        setColour(WHITE)

def success(msg):
    if checkIdle():
        print(msg)
    else:
        setColour(GREEN)
        print(msg)
        setColour(WHITE)

Version = 1.2

print(f"Setting up CMDPlus V{Version}")

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
    Key = r"Software\Policies\Microsoft\Windows\System"
    Reg = ConnectRegistry(None, HKEY_CURRENT_USER)
    CMDDisableKey = OpenKey(Reg, Key)
    CMDDisableVal = QueryValueEx(CMDDisableKey, "DisableCMD")[0]
    if CMDDisableVal == 1:
        error("CMD and scripts are disabled. CMDPlus requires at least batch scripts to be enabled.")
        sleep(5)
        sys.exit(1)
except FileNotFoundError:
    pass

try:
    with open("settings.json", "r") as file:
        Settings = json.load(file)
    SettingsFile = True
    info("Settings file found.")
except (json.decoder.JSONDecodeError, FileNotFoundError) as e:
    error(f"An error has occured.\nError: {e}\nRunning without aliases")
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

success("Setup finished.\nEnter \"exit\" to quit.")

if not checkIdle():
    ctypes.windll.kernel32.SetConsoleTitleW("CMDPlus")

while True:
    UserInput = input(f"CMDPlus: {os.getcwd()}> ")
    Command = UserInput.split(" ")[0].lower()
    AdminMode = False
    if len(Command) == 0:
            print()
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
    elif Command in ["cls", "clear"]:
        clear()
        continue
    try:
        if Command[1] == ":" and Command[0].isalpha():
            os.chdir(Command)
            os.chdir("\\")
            success(f"Changed directory to {os.getcwd()}")
            continue
    except:
        pass
    if Command == "title":
        if checkIdle():
            error("Title command not supported inside IDLE.")
            continue
        ctypes.windll.kernel32.SetConsoleTitleW(" ".join(Args))
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
                    for dirpath, dirnames, filenames in tqdm(os.walk(os.getcwd(), topdown=False), ascii=True, desc="Deletion Progress"):
                        try:
                            os.rmdir(dirpath)
                        except OSError as ex:
                            error(f"Error deleting {dirpath}:\n{ex}")
                    continue
                else:
                    for dirpath, dirnames, filenames in os.walk(os.getcwd(), topdown=False):#
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
                Line = File.readline()
                while Line:
                    print(Line)
                    Line = File.readline()
            success("End of file.")
        except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
            error(f"An error has occured.\nError: {e}")
        continue
    elif Command == "settings":
        if len(Args) == 0:
            info("Current Settings:")
            setColour(LIGHT_BLUE)
            print(f"TQDM Installed: {Settings['tqdm']}")
            success(f"End of settings.")
            continue
        if Args[0].upper() == "TQDM":
            setColour(LIGHT_BLUE)
            print(f"TQDM Installed: {Settings['tqdm']}")
            confirm = input("Do you want to toggle TQDM settings? (Y/N):\n")
            if confirm.upper() in Yes:
                Settings["tqdm"] = not Settings["tqdm"]
                info(f"Changed TQDM settings to: {Settings['tqdm']}")
            else:
                info("Not changing.")
            continue
    elif Command == "exit":
        break
    try:
        output = os.popen(UserInput).read()
        print(output)
    except KeyboardInterrupt:
        error("Keyboard interrupt.\nCommand cancelled.")
        continue

info("Saving changed aliases, settings etc.")
os.chdir(FileLoc)
tmp = {}
tmp["tqdm"] = Settings["tqdm"]
tmp["aliases"] = Settings["aliases"]
with open("settings.json", "w") as File:
    json.dump(tmp, File, indent=4, sort_keys=True)
success("Settings saved. Quitting.")
