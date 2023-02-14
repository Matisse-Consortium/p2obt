import sys
import getpass

from typing import List


def contains_element(list_to_search: List, element_to_search: str) -> bool:
    """Checks if an element is in the list searched and returns 'True' or 'False'

    Parameters
    ----------
    list_to_search: List
        The list to be searched in
    element_to_search: str
        The element being searched for

    Returns
    -------
    element_in_list: bool
        'True' if element is found, 'False' otherwise
    """
    return any([element_to_search in element for element in list_to_search])


def get_password_and_username():
    """Gets the user's ESO-user password to access the p2ui"""
    username = input("Input your ESO-username: ")
    password_prompt = f"Input your ESO-password: "
    if sys.platform == 'ios':
        import console
        password = console.password_alert(password_prompt)
    elif sys.stdin.isatty():
        password = getpass.getpass(password_prompt)
    else:
        password = input()
    return username, password
