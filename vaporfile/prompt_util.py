import sys
import os

def clear_screen():
    os.system('cls' if os.name=='nt' else 'clear')

def get_input(prompt, accept_blank=True):
    try:
        while True:
            response = raw_input(prompt)
            if response == "" and accept_blank==False:
                print("A response is required here.\n")
            else:
                return response
    except KeyboardInterrupt:
        print("\n\nExiting without saving changes.")
        sys.exit(1)
        
def get_yes_no(prompt, yn_ok=True, default=None):
    """Ask the user a Yes or No question.

    yn_ok set to True will allow 'y' or 'n' response too.
    A default may be specified when the user just presses enter."""
    if not prompt.endswith(" "):
        prompt += " "
    while True:
        response = get_input(prompt).lower()
        if response == "yes":
            return True
        elif response == "y" and yn_ok:
            return True
        elif response == "no":
            return False
        elif response == "n" and yn_ok:
            return False
        elif response == "" and default != None:
            return default
        else:
            print("A Yes or No response is required.\n")
