# main.py
# the main file for the expl shell
# (c) 2024 Matto58, licensed under the MIT license

import yaml, os
from colorama import Fore, Back, Style
from getpass import getuser
from socket import gethostname

defaultConfig: dict[str, dict[str]] = {
    "prompt": {
        "showPath": True,
        "showPrevCmdExitCode": True,
        "showUser": False,
        "separator": ">"
    },
    "misc": {
        "showAboutOnStart": True
    }
}

def cmd(ln: list[str]) -> tuple[int, str | None]:
    if ln[0] == "about":
        print(Fore.LIGHTGREEN_EX + "expl version 0.10" + Style.RESET_ALL)
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
    else:
        return (-1, "unknown command: " + ln[0])
    return (0, None)

def loadConfig():
    if not os.path.exists("config.yaml"):
        hconfig = open("config.yaml", "w")
        yaml.dump(defaultConfig, hconfig)
        hconfig.close()
        return defaultConfig
    
    hconfig = open("config.yaml")
    config = yaml.load(hconfig, yaml.Loader)
    hconfig.close()
    return config

def getConfig(config, category, key):
    return config.get(category, defaultConfig[category]).get(key, defaultConfig[category][key])

def main():
    config = loadConfig()
    if getConfig(config, "misc", "showAboutOnStart"): cmd(["about"])
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
                Style.BRIGHT + Fore.BLUE + "/todo/add/path",
                end = Style.RESET_ALL + " "
            )

        line = input(getConfig(config, "prompt", "separator") + " ")
        ln = line.strip().split(" ")
        if len(ln) == 0: continue
        if ln[0] == "exit": return

        (exitCode, errMsg) = cmd(ln)
        if errMsg: print(Fore.RED + "error: " + Style.BRIGHT + errMsg + Style.RESET_ALL)


if __name__ == "__main__": main()
