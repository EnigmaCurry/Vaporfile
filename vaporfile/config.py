import os
import util
import json

from website import S3Website

__config_file__ = os.path.join(os.path.expanduser("~"),".vaporfile")

def load_config(path=None):
    if not path:
        path = __config_file__
    with open(path) as f:
        config = json.loads(f.read())
        try:
            config["websites"]
        except KeyError:
            config["websites"] = {}
    return config

def get_config(path=None):
    """Get the config, load it if possible, create it if necessary"""
    try:
        c = load_config(path)
    except IOError:
        #No existing config, create a new one.
        c = {}
    return c

def save_config(
    config, path=None):
    if not path:
        path = __config_file__
    #JSON is a better pickle:
    with open(path,"w") as f:
        f.write(json.dumps(config,sort_keys=True,indent=4))
    #Make the file read/write only to the user.
    os.chmod(path,00600)
