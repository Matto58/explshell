# i18n.py
# loads translations for the expl shell
# (c) 2024 Matto58, licensed under the MIT license

import yaml
from pathlib import Path
from os.path import isfile

def loadTranslation(langCode: str):
    translationLoc = Path(f"~/.expl/i18n/{langCode}.yaml").expanduser()
    if not isfile(translationLoc):
        return None
    translation = open(translationLoc)
    t = yaml.load(translation, yaml.Loader)
    translation.close()
    return t
