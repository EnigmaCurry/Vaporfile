import os
import util
import json

from website import S3Website

def load_config(path=os.path.join(os.path.expanduser("~"),".vaporfile")):
    with open(path) as f:
        config = json.loads(f.read())
        try:
            config["websites"]
        except KeyError:
            config["websites"] = {}
    return config

def save_config(
    config, path=os.path.join(os.path.expanduser("~"),".vaporfile")):
    #JSON is a better pickle:
    with open(path,"w") as f:
        f.write(json.dumps(config,sort_keys=True,indent=4))
    #Make the file read/write only to the user.
    os.chmod(path,00600)
    
