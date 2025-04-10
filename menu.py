import os

# function to clear the console to enhance userability of the menu system
def clear_console():
    """Clear the console screen."""
    # if Windows
    if os.name == 'nt':
        os.system('cls')
    # if macOS or Linux
    else:
        os.system('clear')

# function to display a menu - accepts a dictionary and prints the heading, the 
# numbers of the menu items and the name of the menu items.
def display_menu(menu):
    print(f"\n{menu['heading']}\n")
    for key, value in menu.items():
        if key != ["heading"]:
            if isinstance(value, tuple):
                label, func = value
                print(f"{key}. {label}" )

# function to create a menu and process user input to select an option. Accpets a 
# menu dictionary, where keys are menu option numbers (as strings) and values are tuples 
# containing a menu description (str) and a function to execute. Optional paramemter - 
# a previous_menu dictionary, to allow navigation back to the previous menu. If no 
# previous_menu is passed as an argument (previous_menu==none) the loop will break 
# after execution, allowing the user to exit the program. 
def create_menu(menu, previous_menu=None):
    clear_console()
    while True:
        display_menu(menu)
        choice = input("\nEnter the corresponding menu number to make a choice: ")
        if choice in menu:
            menu[choice][1]()
            if previous_menu is None:
                break
        else:
            clear_console() 
            print(f"Your input: {choice}\nInvalid choice.")
        
# function to clear the close and print an exit message. Called when the user selects
# 'Exit' from the main menu
def exit_management_system():
    clear_console()
    print("Exiting... ")


