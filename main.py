# main.py
# the main file for the expl shell
# (c) 2024 Matto58, licensed under the MIT license

import os, subprocess, sys
from colorama import Fore, Back, Style
from getpass import getuser
from socket import gethostname
from datetime import datetime
from pathlib import Path
from os.path import isdir, isfile, getsize, getmtime
from shutil import copytree

from i18n import loadTranslation
from config import loadConfig, getConfig

VERSION = "0.21"
YEARS = "2024"
AUTHOR = "Matto58"
REPO_URL = "https://github.com/Matto58/explshell"
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
        aboutText = i18n["about"].split("\n")
        aboutPrint(f"{aboutText[0]} {VERSION}", config)
        if ln.__contains__("--primitive"): return (0, None)
        aboutPrint("\n".join(aboutText[1:]).format(YEARS, AUTHOR, REPO_URL), config)

    elif ln[0] == "clear":
        # https://stackoverflow.com/a/50560686
        print("\033[H\033[J", end="")

    elif ln[0] == "echo":
        print(" ".join(ln[1:]))

    elif ln[0] == "err":
        if len(ln) < 2:
            return (-1, i18n["errMissingErrCode"])
        try:
            return (int(ln[1]), " ".join(ln[2:]) if len(ln) > 2 else None)
        except ValueError:
            return (-1, i18n["errInvalidErrCode"])
        
    elif ln[0] == "cd":
        global path
        if len(ln) < 2:
            print(path)
            return (0, None)
        
        pathL = Path(path)
        pathR = Path(" ".join(ln[1:]))
        newPath = Path(pathL / pathR)

        if not isdir(newPath):
            return (-1, i18n["cdPathNotFound"] + str(newPath))
        path = str(newPath.expanduser().resolve())

    elif ln[0] == "ls":
        thisPath = Path(path) if len(ln) < 2 else Path(" ".join(ln[1:]))
        if not isdir(thisPath):
            return (-1, i18n["lsNotADir"] + str(newPath))
        
        listing = sorted(os.listdir(thisPath))
        # header
        print(Back.LIGHTWHITE_EX + Fore.BLACK + i18n["lsHeader"])
        print(Style.RESET_ALL, end = "")

        dirColor = getattr(Fore, getConfig(config, "colors", "lsDir"))
        flColor = getattr(Fore, getConfig(config, "colors", "lsFile"))
        for p in listing:
            p = Path(thisPath) / p
            if not isdir(p) and not isfile(p): continue # skip symlinks
            # type
            d = isdir(p)
            print((
                dirColor + i18n["lsDir"] if d
                else flColor + i18n["lsFile"]) + "\t", end=Style.RESET_ALL)
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
            process = subprocess.run(ln, stdout=sys.stdout, stdin=sys.stdin, stderr=sys.stderr, cwd=str(path))
            return (process.returncode, None)
        except FileNotFoundError:
            return (-1, i18n["unknownCmd"] + ln[0])
        except KeyboardInterrupt:
            return (-1, None)

    return (0, None)

def main():
    i18nLoc = Path("~/.expl/i18n").expanduser()
    if not isdir(i18nLoc):
        if not isdir("i18n"):
            print("please, for your first run, run the shell with the i18n folder in the same folder as the main file")
            return
        copytree("i18n", i18nLoc)

    config = loadConfig()
    langCode = getConfig(config, "misc", "language")
    
    global i18n
    i18n = loadTranslation(langCode)
    if i18n == None: # ruh roh
        print("could not load translation for " + langCode)
        return

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

        try:
            line = input(getConfig(config, "prompt", "separator"))
        except KeyboardInterrupt:
            print()
            continue
        ln = line.strip().split(" ")
        if len(ln) == 0: continue
        if ln[0] == "exit": return

        (exitCode, errMsg) = cmd(ln, config)
        if errMsg: print(Fore.RED + i18n["error"] + Style.BRIGHT + errMsg + Style.RESET_ALL)


if __name__ == "__main__": main()
