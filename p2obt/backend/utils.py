import re
from typing import List, Tuple

import astropy.units as u


def add_space(input_str: str) -> str:
    """Adds a space to the "HD xxxxxx" targets,
    between the HD and the rest."""
    if re.match(r"^HD\s*\d+", input_str, flags=re.IGNORECASE):
        return re.sub(r"^HD", "HD ", input_str, flags=re.IGNORECASE)
    return input_str


def remove_spaces(input_str: str) -> str:
    """Removes multiple spaces in names (e.g., 'HD  142666')."""
    return re.sub(" +", " ", input_str)


def remove_parenthesis(input_str: str) -> str:
    """Removes parenthesis from a string.

    This if for the ob's name so it is elegible for upload
    (either manually after (.obx)-file creation or automatically.
    """
    return re.sub(r"[\[\](){}]", "", input_str)


# TODO: Reimplement this somehow
def prompt_user(message: str, selections: List[str]) -> str:
    """Prompts the user for a numerical input and returns
    the associated value from the selection list.

    Parameters
    ----------
    message : str
    selections : list of str

    Returns
    -------
    user_input : str
    """
    print(f"Run's {message} could not be automatically detected!")
    choice = ", ".join(
        [f"{index}: {selection}" for index, selection in enumerate(selections, start=1)]
    )
    notice = f"Please input run's {message} ({choice}): "
    return selections[int(input(notice)) - 1]


def contains_element(list_to_search: List, element_to_search: str) -> bool:
    """Checks if an element is in the list searched and returns
    'True' or 'False'

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
    return any(element_to_search in element for element in list_to_search)


def convert_proper_motions(
    *proper_motions: u.mas, rfloat: bool | None = True
) -> Tuple:
    """Converts the proper motions from [mas/yr] to [arcsec/yr].

    Input is assumed to be in [mas], if given as float.
    """
    if all(not isinstance(x, u.Quantity) for x in proper_motions):
        proper_motions = map(lambda x: x * u.mas, proper_motions)
    else:
        raise IOError("Please input proper motions as float or" " astropy.units.mas.")
    proper_motions = u.Quantity([x.to(u.arcsec) for x in proper_motions])
    return proper_motions.value if rfloat else proper_motions
