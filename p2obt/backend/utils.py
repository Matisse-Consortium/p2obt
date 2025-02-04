import re
from typing import Any, Dict, List, Tuple

import astropy.units as u


def replace_elements(
    nested_list: List[List], fill: Any | None = None, default: Any | None = None
) -> List[List]:
    """Replaces all elements in a nested list with a fill value."""
    value = fill if fill is not None and not isinstance(fill, (list, dict)) else default
    for i, item in enumerate(nested_list):
        if isinstance(item, list):
            replace_elements(item, value, default)
        else:
            nested_list[i] = value
    return nested_list


# TODO: Finish this
def create_night_plan_dict(
    targets: List[str] | None = None,
    calibrators: List[List[str] | str] | None = None,
    orders: Dict[str, str] | List[str] | str | None = None,
    tags: Dict[str, str] | List[str] | str | None = None,
    resolution: Dict[str, str] | List[str] | str | None = None,
    configuration: Dict[str, str] | List[str] | str | None = None,
    modes: Dict[str, str] | List[str] | str | None = None,
):
    """Creates a night plan dictionary for the observations.

    targets : list, optional
        A list of targets. If no night plan is given, this list
        and the calibrators must be given.
    calibrators : list, optional
        A list of calibrators that must be given with the targets.
    orders : list, optional
        A list of the orders of the calibrators. If not given,
        it will be assumed that the calibrators are before the targets.
    tags : list, optional
        A list of the tags of the calibrators. If not given, it will
        be "LN" for all calibrators.
    resolution : dict or list of str or str, optional
        A dictionary containing the resolution for each target or a list
        of resolutions for all targets or a single resolution for all targets.
        Will only be used if no night plan is given.
    configurations : dict or list of str or str, optional
        A dictionary containing the array configuration for each target or a list
        of array configurations for all targets or a single array configuration for all targets.
        Will only be used if no night plan is given.
    modes : dict or list of str or str, optional
        A dictionary containing the operational mode for each target or a list
        of operational modes for all targets or a single operational mode for all targets.
        Will only be used if no night plan is given.
    """
    # night_plan = {"run1": }
    if calibrators is None:
        raise IOError("Please input the calibrators.")

    ords = replace_elements(calibrators.copy(), orders, "a")
    tgs = replace_elements(calibrators.copy(), tags, "LN")
    res = replace_elements(targets.copy(), resolution, "low")
    mode = replace_elements(targets.copy(), modes, "gr")

    if isinstance(configuration, str):
        confgs = replace_elements(targets.copy(), configuration)
    else:
        raise IOError("Please input the array configuration.")

    for index, target in enumerate(targets):
        # cals = 
        block = {"name": target.replace(" ", "_"), "mode": mode[index],}
        breakpoint()
    return


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


def convert_proper_motions(*proper_motions: u.mas, rfloat: bool | None = True) -> Tuple:
    """Converts the proper motions from [mas/yr] to [arcsec/yr].

    Input is assumed to be in [mas], if given as float.
    """
    if all(not isinstance(x, u.Quantity) for x in proper_motions):
        proper_motions = map(lambda x: x * u.mas, proper_motions)
    else:
        raise IOError("Please input proper motions as float or" " astropy.units.mas.")
    proper_motions = u.Quantity([x.to(u.arcsec) for x in proper_motions])
    return proper_motions.value if rfloat else proper_motions
