# main.py
# the main file for the expl shell
# (c) 2024 Matto58, licensed under the MIT license

import yaml, os, subprocess, sys
from colorama import Fore, Back, Style
from getpass import getuser
from socket import gethostname
from datetime import datetime
from pathlib import Path
from os.path import isdir, isfile, getsize, getmtime

defaultConfig: dict[str, dict[str]] = {
    "prompt": {
        "showPath": True,
        "showPrevCmdExitCode": True,
        "showUser": False,
        "separator": ">"
    },
    "misc": {
        "startupCommands": ["about --primitive"]
    },
    "colors": {
        "aboutBG": "LIGHTGREEN_EX",
        "aboutFG": "BLACK",
        "lsDir": "LIGHTCYAN_EX",
        "lsFile": "LIGHTRED_EX",
        "user": "LIGHTYELLOW_EX",
        "path": "BLUE",
    }
}
CONFIG_PATH = Path("~/.expl/config.yaml").expanduser()
path = os.getcwd()

def lsFileSize(n: int):
    prefixes = list(" KMGT") # that ought to be enough i suppose
    n2 = float(n)
    for prefix in prefixes:
        if n2 / 1000 < 1:
            return (str(round(n2, 2)) + prefix) if prefix != " " else str(int(n2)) # no prefix should show no decimals
        n2 /= 1000
    return str(round(n2)) + prefix # it's gotta eventually stop

def aboutPrint(s, config={}, end="\n"):
    print(
        getattr(Back, getConfig(config, "colors", "aboutBG"))
        + getattr(Fore, getConfig(config, "colors", "aboutFG"))
        + s + Style.RESET_ALL, end=end)

def cmd(ln: list[str], config) -> tuple[int, str | None]:
    if ln[0] == "about":
        aboutPrint("expl version 0.20", config)
        if ln.__contains__("--primitive"): return (0, None)
        aboutPrint("(c) 2024 Matto58, licensed under the MIT license", config)
        aboutPrint("report issues/contribute at https://github.com/Matto58/explshell", config)
        aboutPrint("thanks for using my silly little shell! <3", config)
    elif ln[0] == "clear":
        # https://stackoverflow.com/a/50560686
        print("\033[H\033[J", end="")
    elif ln[0] == "echo":
        print(" ".join(ln[1:]))
    elif ln[0] == "err":
        if len(ln) < 2:
            return (-1, "missing error code parameter")
        try:
            return (int(ln[1]), " ".join(ln[2:]) if len(ln) > 2 else None)
        except ValueError:
            return (-1, "invalid error code")
    elif ln[0] == "cd":
        global path
        if len(ln) < 2:
            print(path)
            return (0, None)
        
        pathL = Path(path)
        pathR = Path(" ".join(ln[1:]))
        newPath = Path(pathL / pathR)

        if not isdir(newPath):
            return (-1, "path not found: " + str(newPath))
        path = str(newPath.expanduser().resolve())
    elif ln[0] == "ls":
        thisPath = Path(path) if len(ln) < 2 else Path(" ".join(ln[1:]))
        if not isdir(thisPath):
            return (-1, "not a directory: " + str(newPath))
        
        listing = sorted(os.listdir(thisPath))
        # header
        print(Back.LIGHTWHITE_EX + Fore.BLACK + "Type\tSize\tLast modified\tName")
        print(Style.RESET_ALL, end = "")

        dirColor = getattr(Fore, getConfig(config, "colors", "lsDir"))
        flColor = getattr(Fore, getConfig(config, "colors", "lsFile"))
        for p in listing:
            p = Path(thisPath) / p
            if not isdir(p) and not isfile(p): continue # skip symlinks
            # type
            d = isdir(p)
            print((
                dirColor + "Dir" if d
                else flColor + "File") + "\t", end=Style.RESET_ALL)
            # size
            size = getsize(p)
            print("" if d else lsFileSize(size), end="\t")
            # last modified
            lastmod = datetime.fromtimestamp(getmtime(p))
            print(f"D{(lastmod.year % 100):02}{lastmod.month:02}{lastmod.day:02}", end="\t") # date YYMMDD
            print(f"T{lastmod.hour:02}{lastmod.minute:02}{lastmod.second:02}", end="\t") # time HHMMSS
            # name
            print((dirColor if d else flColor) + p.name + Style.RESET_ALL)

    else:
        try:
            process = subprocess.run(ln, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr)
            return (process.returncode, None)
        except FileNotFoundError:
            return (-1, "unknown command: " + ln[0])
    return (0, None)

def loadConfig():
    if not os.path.exists(CONFIG_PATH.parent):
        os.mkdir(CONFIG_PATH.parent)
    if not os.path.exists(CONFIG_PATH):
        hconfig = open(CONFIG_PATH, "w")
        yaml.dump(defaultConfig, hconfig)
        hconfig.close()
        return defaultConfig
    
    hconfig = open(CONFIG_PATH)
    config = yaml.load(hconfig, yaml.Loader)
    hconfig.close()
    return config

def getConfig(config, category, key):
    return config.get(category, defaultConfig[category]).get(key, defaultConfig[category][key])

def main():
    config = loadConfig()
    for command in getConfig(config, "misc", "startupCommands"):
        cmd(command.split(" "), config)
    exitCode = None
    while True:
        if getConfig(config, "prompt", "showPrevCmdExitCode"):
            print(
                "" if exitCode == None
                else Fore.GREEN + "0 " if exitCode == 0
                else Fore.RED + str(exitCode) + " ",
                end = Style.RESET_ALL
            )
        if getConfig(config, "prompt", "showUser"):
            print(
                Fore.LIGHTYELLOW_EX + getuser() + "@" + gethostname(),
                end = Style.RESET_ALL + " "
            )
        if getConfig(config, "prompt", "showPath"):
            print(
                Style.BRIGHT + Fore.BLUE + path,
                end = Style.RESET_ALL
            )

        line = input(getConfig(config, "prompt", "separator"))
        ln = line.strip().split(" ")
        if len(ln) == 0: continue
        if ln[0] == "exit": return

        (exitCode, errMsg) = cmd(ln, config)
        if errMsg: print(Fore.RED + "error: " + Style.BRIGHT + errMsg + Style.RESET_ALL)


if __name__ == "__main__": main()
