"""Automated OB Creation

This script creates the OBs from either a manual input list a manual input
dictionary, or a (.yaml)-file and makes folders corresponding to the structure
of the MATISSE observations on the P2

DISCLAIMER: Standalone only works for the UTs at the moment and for ATs it
            shows keyerror

This file can also be imported as a module and contains the following functions:

    * load_yaml - Loads a (.yaml)-file into a dictionary (compatible/superset
    with/of (.json)-format/file)
    * get_night_name_and_date - Quality of life function that gets the night's
    name and date and names
    * get_array - Automatically gets the array config if possible and if not
    prompts the user to input it
    * make_sci_obs - Makes the SCI-OBs
    * make_cal_obs - Makes the CAL-OBs
    * read_dict_into_OBs - Reads either a (.yaml)-file or a Dict into a format
    suitable for OB creation
    * ob_creation - The main loop for OB creation

Example of usage:

    >>> from automatedOBcreation import ob_pipeline

    Script needs either manual_lst, path2file (to the parsed night plan) in
    (.yaml)-file format or run_data (the parsed night plan without it being
    saved)

    >>> path2file = "night_plan.yaml"

    or

    >>> from parseOBplan import parse_night_plan
    >>> run_data = parse_night_plan(...)

    Calibration lists accept sublists (with more than one item)
    but also single items, same for tag_lst

    >>> sci_lst = ["AS 209", "VV Ser"]
    >>> cal_lst = [["HD 142567", "HD 467893"], ["HD 142567"]]
    >>> tag_lst = [["LN", "N"], "L"]
    >>> manual_lst = [sci_lst, cal_lst, tag_lst]

    Specifies the paths, where the (.obx)-files are saved to, name of run can
    be changed to actual one

    >>> outdir = "..."

    Specifies the 'res_dict'. Can be left empty. Changes only L-band res at
    the moment.
    Resolutions are 'LOW', 'MED', 'HIGH'

    >>> res_dict = {"AS 209": "MED"}

    The main OB creation
    Either with 'path2file' (saved (.yaml)-file)

    >>> ob_creation(outpath, path2file=path2file, res_dict=res_dict, mode="gr")

    Or with 'run_data' (parsed (.yaml)-dictionary)

    >>> ob_creation(outpath, run_data=run_data, res_dict=res_dict, mode="gr")

    Or with 'manual_lst' (List input by hand)

    >>> ob_creation(outpath, manual_lst=manual_lst, res_dict=res_dict, mode="gr")
    # ... Making OBs for run 1, 109.2313.001 = 0109.C-0413(A), ATs small array
    # ... Creating folder: 'night1_May25', and filling it with OBs
    # ... SCI HD 142527         15:56:41.888  -42:19:23.248   4.8      9.8   5.0   8.3
"""
import time
import logging
from pathlib import Path
from typing import Union, Optional, Any, Dict, List, Tuple

import numpy as np

from .create import create_ob

OPERATIONAL_MODES = {"both": ["standalone", "GRA4MAT"],
                     "st": ["standalone"], "gr": ["GRA4MAT"]}

def copy_list_and_replace_all_values(input_list: List, value: Any):
    """Replaces all values in list with the given value. Takes into account nested lists

    Parameters
    ----------
    input_list: List
        An input list of any form. May contain once nested lists
    value: Any
        Any value that will make up the new list

    Returns
    -------
    output_list: List
        The input_list with all its values replaced by the given value
    """
    output_list = input_list.copy()
    for index, element in enumerate(input_list):
        if isinstance(element, list):
            for sub_index, _ in enumerate(element):
                output_list[index][sub_index] = value
        else:
            output_list[index] = value
    return output_list


def get_night_name_and_date(night_name: str) -> str:
    """Automatically gets the night's date if it is included in the
    dictionary

    Parameters
    ----------
    night_key : str
        The dictionaries key that describes a night

    Returns
    -------
    night_name : str
        If night date in night then of the format <night>_<night_date> if not
        then <night>
    """
    if "full" in night_name:
        return night_name

    night = night_name.split(":")[0].strip()
    date = night_name.split(":")[1].split(",")[0].strip()

    # TODO: Write down how the nights need to be written down in the observing plan
    if len(night.split()) > 2:
        try:
            night, date = night.split(",")[:2]
        except ValueError:
            return night

    return "_".join([''.join(night.split()), ''.join(date.split())])\
            if date != '' else ''.join(night.split())


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
    choice = ', '.join([f'{index}: {selection}'
        for index, selection
        in enumerate(selections, start=1)])
    notice = f"Please input run's {message} ({choice}): "
    return selections[int(input(notice))-1]


def get_array_config(run_name: Optional[str] = None) -> str:
    """Fetches the array configuration from the name of the run. And if no run
    name is specified or no match can be found prompts the user for the
    configuration

    Parameters
    ----------
    run_name: str, optional
        The name of the run

    Returns
    -------
    array_configuration: str
    """
    if run_name:
        if "UTs" in run_name:
            array_configuration =  "UTs"
        elif ("ATs" in run_name) or any([config in run_name for config in AT_CONFIG]):
            if "small" in run_name:
                array_configuration = "small"
            elif "medium" in run_name:
                array_configuration = "medium"
            else:
                array_configuration = "large"
    else:
        array_configuration = prompt_user("array_configuration",
                                          ["small", "medium", "large",
                                           "extended", "UTs"])
    return array_configuration


# TODO: Make this more robust with the parser looking through all of the run for the
# resolution and writing it in the yaml file
def get_run_resolution(run_name: str) -> str:
    """Gets the run's resolution from the run's name"""
    if "LR" in run_name:
        resolution = "LOW"
    elif "MR" in run_name:
        resolution = "MED"
    elif "HR" in run_name:
        resolution = "HIGH"
    else:
        resolution = prompt_user("resolution", ["LOW", "MED", "HIGH"])
    return resolution


def get_run_operational_mode(run_name: str) -> str:
    """Gets the run's used instrument, MATISSE or GRA4MAT"""
    if "GRA4MAT" in run_name:
        operational_mode = "gr"
    elif "MATISSE" in run_name:
        operational_mode = "st"
    else:
        operational_mode = prompt_user("instrument",
                                     ["matisse", "gra4mat"]) 
    return operational_mode


def make_sci_obs(targets: List[str], array_config: str,
                 operational_mode: str, output_dir: str,
                 res_dict: Dict, resolution: str) -> None:
    """Gets the inputs from a list and calls the 'mat_gen_ob' for every
    list element.

    Parameters
    ----------
    targets : list of str
        Contains the science objects.
    array_config : str
        The array configuration ("small", "medium", "large", "extended")
        or "UTs".
    operational_mode : str
        The mode of operation of MATISSE.
    output_dir : str
        The output directory, where the '.obx'-files will be created in.
    resolution : str
        The spectral resolution for the L-band.
    """
    for target in targets:
        create_ob(target, "sci", array_config, operational_mode,
                  resolution=resolution, output_dir=output_dir)


# TODO: Make these functions more compact
def make_cal_obs(calibrators: Union[List[str], List[List[str]]],
                 targets: List[str], tags: List[str], orders: List[str],
                 array_config: str, operational_mode: str,
                 output_dir: Path, resolution: str) -> None:
    """Checks if there are sublists in the calibration list and calls the 'mat_gen_ob'
    with the right inputs to generate the calibration objects.

    The input lists correspond to each other index-wise (e.g., cal_lst[1], sci_lst[1],
                                                         tag_lst[1]; etc.)
    The calibrators list also accepts nested lists for multiple calibrators for a science
    target

    Parameters
    ----------
    calibrators: list of str or list of list of str
        Contains the calibration objects corresponding to the science objects
    targets : list of str
        Contains the science objects
    tags: list of str
        Contains the tags (either 'L', 'N', or both) and corresponds to the science
        objects
    order : list
        Contains the order if the calibrator is before "b" or after "a" the science
        target
    array_config : str
        The array configuration ('small', 'medium', 'large') or 'UTs'
    operational_mode : str
        The mode MATISSE is operated in and for which the OBs are created.
        Either 'st' for standalone, 'gr' for GRA4MAT_ft_vis or 'both',
        if OBs for both are to be created
    output_dir : path
        The output directory, where the '.obx'-files will be created in
    resolution : List, optional
        The default spectral resolutions for l- and n-band. set to LOW for the UTs
        and to MED for the ATs as a default
    """
    # TODO: Fix if resolution dict is input then target gets put into the wrong mode
    for calibrator, target, tag, order in zip(calibrators, targets, tags, orders):
        # try:
        if isinstance(calibrator, list):
            for cal, ord, sub_tag in zip(calibrator, order, tag):
                create_ob(cal, "cal", array_config, operational_mode,
                          sci_name=target, tag=sub_tag,
                          resolution=resolution, output_dir=output_dir)
                # logging.info(f"Created OB CAL-{cal}")
        else:
            create_ob(calibrator, "cal", array_config,
                      operational_mode, sci_name=target, tag=tag,
                      resolution=resolution, output_dir=output_dir)
                # logging.info(f"Created OB CAL-{calibrator}")

        # except Exception:
            # logging.error(f"Skipped OB: CAL-{calibrator}", exc_info=True)
            # print(f"ERROR: Skipped OB: CAL-{calibrator} -- Check 'creator.log'-file")


def read_dict_to_lists(night: Dict) -> Tuple[List[Any]]:
    """Reads the data of the night plan contained in a dictionary
    into the four lists (targets, calibrators, order and tags)."""
    target_lst, calibrator_lst, order_lst, tag_lst = [], [], [], []
    for science_target, calibrators in night.items():
        target_lst.append(science_target)
        if len(calibrators) == 1:
            calibrator_lst.append(calibrators[0]["name"])
            order_lst.append(calibrators[0]["order"])
            tag_lst.append(calibrators[0]["tag"])
        else:
            cal_info = np.array([(calibrator["name"],
                                  calibrator["order"],
                                  calibrator["tag"])
                                for calibrator in calibrators])
            calibrator_lst.append(cal_info[:, 0].tolist())
            order_lst.append(cal_info[:, 1].tolist())
            tag_lst.append(cal_info[:, 2].tolist())
    return target_lst, calibrator_lst, order_lst, tag_lst


def create_obs_from_lists(sci_lst: List, cal_lst: List, order_lst: List,
                          tag_lst: List, operational_mode: str,
                          output_dir: Path, array_config: str,
                          res_dict: Dict, standard_res: List) -> None:
    """"""
    for mode in OPERATIONAL_MODES[operational_mode]:
        # TODO: Exchange these print statements
        print("-----------------------------")
        print(f"Creating OBs for {mode}-mode...")
        print("-----------------------------")
        if not tag_lst:
            tag_lst = copy_list_and_replace_all_values(cal_lst, "LN")
        if not order_lst:
            order_lst = copy_list_and_replace_all_values(cal_lst, "a")

        mode_out_dir = output_dir / mode
        if not mode_out_dir.exists():
            mode_out_dir.mkdir(parents=True, exist_ok=True)

        # TODO: Add res-dict back in and set the resolution then
        make_sci_obs(sci_lst, array_config, mode,
                     mode_out_dir, res_dict, standard_res)
        make_cal_obs(cal_lst, sci_lst, tag_lst, order_lst, array_config,
                     mode, mode_out_dir, standard_res)


def create_obs_from_dict(operational_mode: str,
                         night_plan: Dict,
                         output_dir: Optional[Path] = None,
                         res_dict: Optional[Dict] = None,
                         resolution: Optional[str] = "low",
                         observation_mode: Optional[str] = "vm") -> None:
    """This reads either the (.yaml)-file into a format suitable for the Jozsef
    Varga's OB creation code or reads out the run dict if 'run_data' is given,
    and subsequently makes the OBs.

    Also automatically gets the array_config from the run name and if not
    possible then prompts the user to input it

    Parameters
    ----------
    operational_mode : str
        The mode MATISSE is operated in and for which the OBs are created.
        Either 'st' for standalone, 'gr' for GRA4MAT_ft_vis or 'both',
        if OBs for both are to be created
    night_plan : dict
    outpath: Path
        The output path
    res_dict: Dict, optional
        A dict with entries corresponding to non low-resolution
    standard_res: List, optional
        The default spectral resolutions for L- and N-band. By default it is set
        to medium for L- and low for N-band
    """
    # TODO: Write down how the runs need to be written down in the observing plan -> Make
    # it automatic at some point
    for run_id, run in night_plan.items():
        print("-----------------------------")
        print(f"Creating OBs for {run_id}...")
        # logging.info(f"Creating OBs for '{run_id}'...")

        if observation_mode == "sm":
            standard_res = get_run_resolution(run_id)
            operational_mode = get_run_operational_mode(run_id)

        run_name = ''.join(run_id.split(",")[0].strip().split())
        run_dir = output_dir / run_name
        if not run_dir.exists():
            run_dir.mkdir(parents=True, exist_ok=True)
        # logging.info(f"Creating folder '{run_name}...'")

        array_config = get_array_config(run_id)
        for night_id, night in run.items():
            night_name = get_night_name_and_date(night_id)
            night_dir = run_dir / night_name
            if not night_dir.exists():
                night_dir.mkdir(parents=True, exist_ok=True)

            print("-----------------------------")
            print(f"Creating folder: '{night_dir.name}', and filling it with OBs...")
            # logging.info(f"Creating folder: '{night_dir.name}', and filling it with OBs")

            # NOTE: This avoids a timeout from the query-databases (such as Vizier)
            create_OBs_from_lists(*read_dict_to_lists(night), operational_mode,
                                  night_dir, array_config, res_dict, standard_res)


def ob_creation(output_dir: Path,
                sub_folder: Optional[Path] = None,
                night_plan: Optional[Dict] = None,
                manual_lst: Optional[List] = None,
                res_dict: Optional[Dict] = None,
                standard_res: Optional[List] = None,
                operational_mode: str = "st",
                observation_mode: Optional[str] = "visitor",
                clean_previous: bool = False) -> None:
    """Gets either information from a 'nigh_plan.yaml'-file or a dictionary contain the
    run's data. Then it checks a dictionary for the resolution input for specific science
    targets and generates the OBS. Uses a standard resolution if none is provided.

    Parameters
    ----------
    output_dir: Path
    sub_folder: Path, optional
        A sub-folder in which the scripts are made into (if manually given)
    night_plan: Dict
        The data that would be saved to a 'night_plan.yaml'-file
    manual_lst: List, optional
        The manual input of the four needed lists [targets, calibrators, tags, order].
        Only the targets and calibrators list need to be provided, tags and order can
        be autofilled.
        If this is given the path of execution will be 'output_dir / "manualOBs"'
    resolution_dict: Dict, optional
        A dict with entries corresponding the resolution of specific science targets
    standard_res: List, optional
        The default spectral resolutions for L- and N-band. By default it is set
        to medium for L- and low for N-band
    mode_selection: str
        The mode MATISSE is operated in and for which the OBs are created.
        Either 'st' for standalone, 'gr' for GRA4MAT_ft_vis or 'both',
        if OBs for both are to be created
    observation_mode: str, optional
        Can either be "visitor" for Visitor Mode (VM) or "service" for Service Mode (SM)
    clean_previous: bool
        If toggled will remove the path given/in which the OBs are to be created
        DISCLAIMER: Danger this will remove all subfolders and data contined in it
    """
    output_dir = Path(output_dir, "manualOBs")\
            if manual_lst else Path(output_dir, "automaticOBs")

    if manual_lst is not None:
        if sub_folder is not None:
            output_dir /= sub_folder
        array_config = get_array_config()
        try:
            sci_lst, cal_lst, tag_lst, order_lst = manual_lst
        except ValueError as exc:
            raise ValueError("In case of manual input four lists "
                             " (science_targets, calibrators, orders, tag)"
                             " must be given!") from exc
        create_obs_from_lists(sci_lst, cal_lst, order_lst, tag_lst,
                              operational_mode, output_dir, array_config,
                              res_dict, standard_res)

    elif night_plan is not None:
        create_obs_from_dict(operational_mode, night_plan, output_dir,
                             res_dict, standard_res, observation_mode)
    else:
        raise IOError("Neither '.yaml'-file nor input list found or input"
                      " dict found!")

    # TODO: Add this back into the function
    # if clean_previous:
        # confirmation = input(f"You are trying to remove\n'{output_dir}'\n"
                             # "THIS CANNOT BE REVERSED! Are you sure? (yN): ")
        # if confirmation.lower() == "y":
            # shutil.rmtree(output_dir)
            # print("Files were cleaned up!")
        # else:
            # print("Files not cleaned up!")
#


if __name__ == "__main__":
    path = "night_plan.yaml"
    outdir = Path("/Users/scheuck/Data/observations/obs/")

    sci_lst = ["Beta Leo", "HD 100453"]
    cal_lst = ["HD100920", "HD102964"]
    tag_lst = []

    # TODO: Make explanation/docs of the order_lst
    order_lst = []

    manual_lst = [sci_lst, cal_lst, tag_lst, order_lst]

    res_dict = {}

    # TODO: Add mode that 45 mins med and 30 mins med works? with the new double templates
    # /OBs
    # TODO: Make better error messages (in case of specific failure -> then log)

    # TOOD: Add night astronomer comments to template of Jozsefs -> Rewrite his script?
    # TODO: Find way to switch of photometry of template -> Jozsef's script rewrite?

    ob_creation(outdir, sub_folder=None, manual_lst=manual_lst,
                res_dict=res_dict, operational_mode="both",
                standard_res="low", clean_previous=False)


    # TODO: Include this somewhere
    # run_prog_id = None
    # for element in run_name.split():
    #     if len(element.split(".")) == 3:
    #         run_prog_id = element
    #         break

