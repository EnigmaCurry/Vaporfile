import sys
import os.path
import json
import base64
import getpass

import config
from prompt_util import clear_screen, get_input

class VaporfileCredentialException(Exception):
    pass

def prompt_save_credentials(args):
    clear_screen()
    print(" WARNING WARNING WARNING ".center(80,"+"))
    print("This will save your Amazon AWS credentials in your home directory.")
    print("The file ~/.vaporfile will be readable only by your user account.")
    print("It is still your responsibility to secure your computer from unwanted")
    print("access. This should be perfectly safe contingent upon proper system security.")
    print("".center(80,"+"))
    print("")
    print("For reference, your amazon credentials can be found at:")
    print("https://aws-portal.amazon.com/gp/aws/developer/account/index.html?action=access-key")
    print("")
    cred = {"access_key":get_input("What is your Access key? : ",accept_blank=False),
            "secret_key":get_input("What is your Secret key? : ",accept_blank=False)}
    print("")
    store_credentials(cred)
    clear_screen()
    print("Credentials saved in ~/.vaporfile")
    print("File access restricted to your user account ({0}).".format(getpass.getuser()))
    print("")

def check_credentials(user_config=None):
    if not user_config:
        user_config = config.get_config()
    try:
        user_config["credentials"]["access_key"]
        user_config["credentials"]["secret_key"]
    except KeyError:
        raise VaporfileCredentialException(
            "Missing Amazon credentials in config")
    return True
    
def store_credentials(credentials):
    """Store Amazon AWS credentials in user's home directory"""
    c = config.get_config()
    c["credentials"] = credentials
    config.save_config(c)

def remove_credentials(credentials):
    """Store Amazon AWS credentials in user's home directory"""
    c = config.get_config()
    del c["credentials"]
    config.save_config(c)
    
