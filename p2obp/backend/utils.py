import sys
import getpass
from typing import Optional, Tuple, List

import astropy.units as u


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
    password_prompt = "Input your ESO-password: "
    if sys.platform == 'ios':
        import console
        password = console.password_alert(password_prompt)
    elif sys.stdin.isatty():
        password = getpass.getpass(password_prompt)
    else:
        password = input()
    return username, password


def convert_proper_motions(*proper_motions: u.mas,
                           rfloat: Optional[bool] = True) -> Tuple:
    """Converts the proper motions from [mas/yr] to [arcsec/yr].

    Input is assumed to be in [mas], if given as float.
    """
    if all(not isinstance(x, u.Quantity) for x in proper_motions):
        proper_motions = map(lambda x: x*u.mas, proper_motions)
    else:
        raise IOError("Please input proper motions as float or"
                      " astropy.units.mas.")
    proper_motions = u.Quantity([x.to(u.arcsec) for x in proper_motions])
    return proper_motions.value if rfloat else proper_motions


if __name__ == "__main__":
    print(convert_proper_motions(1.28, 1.278))
