
import string

import os


def clear_console():
    """Clear the console screen."""
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For macOS and Linux
    else:
        os.system('clear')

def display_menu(menu):
    print(f"\n{menu['heading']}\n")
    for key, value in menu.items():
        if key != ["heading"]:
            if isinstance(value, tuple):
                label, func = value
                print(f"{key}. {label}" )

def create_menu(menu, previous_menu=None):
    while True:
        display_menu(menu)
        choice = input("\nEnter the corresponding menu number to make a choice: ")
        if choice in menu:
            menu[choice][1]()
            if previous_menu is None:
                break
        else:
            clear_console() 
            print(choice + "\nInvalid choice.\n")
        



def exit_management_system():
    clear_console()
    print("Exiting... ")


