# config.py
# the config manager for expl
# (c) 2024 Matto58, licensed under the MIT license

import os, yaml
from pathlib import Path

defaultConfig = {
    "prompt": {
        "showPath": True,
        "showPrevCmdExitCode": True,
        "showUser": False,
        "separator": ">"
    },
    "misc": {
        "startupCommands": ["about --primitive"],
        "language": "en"
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