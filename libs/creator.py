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
import os
import time
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Tuple, Optional

import numpy as np
import yaml

import MATISSE_create_OB_2 as ob

# NOTE: Make this work for N-band as well -> Right now not needed for the observations
# FIXME: Check back with Jozsef and or how to act if H_mag error occurs, or
# other script related errors


# TODO: Make logs being created in p2obp folder in documents or so on the long run
LOG_PATH = Path(__file__).parent / "logs/creator.log"

if LOG_PATH.exists():
    os.remove(LOG_PATH)
else:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.touch()

logging.basicConfig(filename=LOG_PATH, filemode='w',
                    format='%(asctime)s - %(message)s', level=logging.INFO)

# TODO: Overhaul all the functions defaults and annotiations, add better documentation as
# well
# NOTE: Dictionaries for the template- and resolution-configurations
# NOTE: For the UTs/ATs in standalone there is only one resolution as of yet -> Maybe
# change in the future. The higher ones, to avoid errors are the same
UT_DICT_STANDALONE = {"ACQ": ob.acq_tpl,
                      "LOW": {"TEMP": [ob.obs_tpl], "DIT": [0.111],
                              "RES": ["L-LR_N-LR"]},
                      "MED": {"TEMP": [ob.obs_tpl], "DIT": [0.111],
                              "RES": ["L-LR_N-LR"]},
                      "HIGH": {"TEMP": [ob.obs_tpl], "DIT": [0.111],
                              "RES": ["L-LR_N-LR"]}}

AT_DICT_GRA4MAT = {"ACQ": ob.acq_ft_tpl,
                   "LOW": {"TEMP": [ob.obs_ft_tpl], "DIT": [0.6], "RES":
                           ["L-LR_N-LR"]},
                   "MED": {"TEMP": [ob.obs_ft_tpl],
                           "DIT": [1.3], "RES": ["L-MR_N-LR"]},
                   "HIGH": {"TEMP": [ob.obs_ft_tpl],
                           "DIT": [3.], "RES": ["L-HR_N-LR"]}}

# NOTE: Maybe include the higher resolutions again at some point
UT_DICT_GRA4MAT = {"ACQ": ob.acq_ft_tpl,
                   "LOW": {"TEMP": [ob.obs_ft_tpl], "DIT": [0.111], "RES":
                           ["L-LR_N-LR"]},
                   # "LOW_VIS": {"TEMP": [ob.obs_ft_vis_tpl], "DIT": [0.111], "RES":
                               # ["L-LR_N-LR"]},
                   # "MED": {"TEMP": [ob.obs_ft_coh_tpl, ob.obs_ft_vis_tpl],
                           # "DIT": [1.3, 0.111], "RES": ["L-MR_N-LR"]},
                   # "HIGH": {"TEMP": [ob.obs_ft_coh_tpl, ob.obs_ft_vis_tpl],
                           # "DIT": [3., 0.111], "RES": ["L-HR_N-LR"]}
                  }

TEMPLATE_RES_DICT = {"standalone": {"UTs": UT_DICT_STANDALONE, "ATs": UT_DICT_STANDALONE},
                     "GRA4MAT": {"UTs": UT_DICT_GRA4MAT, "ATs": AT_DICT_GRA4MAT}}

AT_CONFIG = ["small", "medium", "large", "astrometric"]
TEL_CONFIG = ["UTs", *AT_CONFIG]


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


def add_order_tag_to_newest_file(outdir: Path, order_tag: str):
    """Fetches the last created file and adds and order tag to it"""
    latest_file = max(outdir.glob("*.obx"), key=os.path.getctime)
    latest_file.rename(latest_file.with_stem(latest_file.stem + f"-{order_tag}"))


def get_night_name_and_date(night_name: str) -> str:
    """Automatically gets the night's date if it is included in the
    dictionary

    Parameters
    ----------
    night_key: str
        The dictionaries key that describes a night

    Returns
    -------
    night_name: str
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
            return "UTs"
        elif ("ATs" in run_name) or any([config in run_name for config in AT_CONFIG]):
            if "small" in run_name:
                return "small"
            elif "medium" in run_name:
                return "medium"
            else:
                return "large"
        else:
            user_inp = int(input("No configuration can be found, please input"\
                             " ('UTs': 1; 'small': 2, 'medium': 3, 'large/astrometric: 4): "))-1
            return TEL_CONFIG[user_inp]
    else:
        user_inp = int(input("No configuration can be found, please input"\
                         " ('UTs': 1; 'small': 2, 'medium': 3, 'large/astrometric: 4): "))-1
        return TEL_CONFIG[user_inp]


def write_run_prog_id(run_id: str, output_dir: Path) -> None:
    """"""
    prog_id = None
    for element in run_id.split():
        try:
            if len(element.split(".")) == 3:
                prog_id = element
        except:
            continue
    # TODO: Maybe add a while loop here for wrong input. Do the same above?
    if prog_id is None:
        print("Run's id could not be automatically detected!")
        prog_id = input("Please enter the run's id in the following form"
                        " (<period>.<program>.<run> (e.g., 110.2474.004)): ")

    # TODO: Maybe extend this as a (.toml)-file or so
    with open(output_dir / "run_id.txt", "w+") as run_id_file:
        run_id_file.write(prog_id)
    print("[INFO] Run's id has been written to 'run_id.txt'")


def make_sci_obs(targets: List, array_config: str,
                 mode: str, output_dir: str,
                 res_dict: Dict, standard_resolution: List) -> None:
    """Gets the inputs from a list and calls the 'mat_gen_ob' for every list element

    Parameters
    ----------
    targets: list
        Contains the science objects
    array_config: str
        The array configuration ('small', 'medium', 'large') or 'UTs'
    mode: str
        The mode of operation of MATISSE
    out_dir: str
        The output directory, where the '.obx'-files will be created in
    standard_resolution: List
        The default spectral resolutions for L- and N-band. Set to low for both
        as a default
    """
    array_key = "UTs" if array_config == "UTs" else "ATs"
    template = TEMPLATE_RES_DICT[mode][array_key]
    acquisition = template["ACQ"]

    if standard_resolution is None:
        standard_resolution = "LOW"

    for index, target in enumerate(targets, start=1):
        try:
            if res_dict and (target in res_dict):
                temp = SimpleNamespace(**template[res_dict[target]])
            else:
                temp = SimpleNamespace(**template[standard_resolution])

            ob.mat_gen_ob(target, array_config, 'SCI',
                          outdir=str(output_dir), spectral_setups=temp.RES,
                          obs_tpls=temp.TEMP, acq_tpl=acquisition, DITs=temp.DIT)
            add_order_tag_to_newest_file(output_dir, index)

            logging.info(f"Created OB: SCI-{target}")

        except Exception:
            logging.error(f"Skipped OB: SCI-{target}", exc_info=True)
            print(f"ERROR: Skipped OB: SCI-{target} -- Check 'creator.log'-file")


# TODO: Make these functions more compact
def make_cal_obs(calibrators: List, targets: List, tags: List,
                 orders: List, array_config: str, mode_selection: str,
                 output_dir: Path, resolution_dict: Optional[Dict] = {},
                 standard_resolution: Optional[List] = None) -> None:
    """Checks if there are sublists in the calibration list and calls the 'mat_gen_ob'
    with the right inputs to generate the calibration objects.

    The input lists correspond to each other index-wise (e.g., cal_lst[1], sci_lst[1],
                                                         tag_lst[1]; etc.)
    The calibrators list also accepts nested lists for multiple calibrators for a science
    target

    Parameters
    ----------
    calibrators: List
        Contains the calibration objects corresponding to the science objects
    targets: List
        Contains the science objects
    tags: List
        Contains the tags (either 'L', 'N', or both) and corresponds to the science
        objects
    order: List
        Contains the order if the calibrator is before "b" or after "a" the science
        target
    array_config: str
        The array configuration ('small', 'medium', 'large') or 'UTs'
    mode_selection: str
        The mode MATISSE is operated in and for which the OBs are created.
        Either 'st' for standalone, 'gr' for GRA4MAT_ft_vis or 'both',
        if OBs for both are to be created
    output_dir: Path
        The output directory, where the '.obx'-files will be created in
    resolution_dict: Dict, optional
    standard_res: List, optional
        The default spectral resolutions for l- and n-band. set to LOW for the UTs
        and to MED for the ATs as a default
    """
    array_key = "UTs" if array_config == "UTs" else "ATs"
    template = TEMPLATE_RES_DICT[mode_selection][array_key]
    acquisition = template["ACQ"]

    if not standard_resolution:
        standard_resolution = "LOW"

    # TODO: Fix if resolution dict is input then target gets put into the wrong mode
    for calibrator, target, tag, order in zip(calibrators, targets, tags, orders):
        try:
            if resolution_dict and (target in resolution_dict):
                calibrator_template =\
                        SimpleNamespace(**template[resolution_dict[target]])
            else:
                calibrator_template = SimpleNamespace(**template[standard_resolution])

            # TODO: Remove the str(output_dir) at some point after Jozsef's code rewrite
            if isinstance(calibrator, list):
                for cal, ord, sub_tag in zip(calibrator, order, tag):
                    ob.mat_gen_ob(cal, array_config, 'CAL', outdir=str(output_dir),
                                  spectral_setups=calibrator_template.RES,
                                  obs_tpls=calibrator_template.TEMP,
                                  acq_tpl=acquisition, sci_name=target, tag=sub_tag,
                                  DITs=calibrator_template.DIT)
                    add_order_tag_to_newest_file(output_dir, ord)
                    logging.info(f"Created OB CAL-{cal}")
            else:
                ob.mat_gen_ob(calibrator, array_config, 'CAL', outdir=str(output_dir),
                              spectral_setups=calibrator_template.RES,
                              obs_tpls=calibrator_template.TEMP,
                              acq_tpl=acquisition, sci_name=target, tag=tag,
                              DITs=calibrator_template.DIT)
                add_order_tag_to_newest_file(output_dir, order)
                logging.info(f"Created OB CAL-{calibrator}")

        except Exception:
            logging.error(f"Skipped OB: CAL-{calibrator}", exc_info=True)
            print(f"ERROR: Skipped OB: CAL-{calibrator} -- Check 'creator.log'-file")


def read_dict_to_lists(night: Dict) -> Tuple[List[Any]]:
    """Reads the data of the night plan contained in a dictionary into the four lists"""
    target_lst, calibrator_lst, order_lst, tag_lst = [], [], [], []
    for science_target, calibrators in night.items():
        target_lst.append(science_target)
        if len(calibrators) == 1:
            calibrator_lst.append(calibrators[0]["name"])
            order_lst.append(calibrators[0]["order"])
            tag_lst.append(calibrators[0]["tag"])
        else:
            cal_info = np.array([(calibrator["name"], calibrator["order"], calibrator["tag"])\
                    for calibrator in calibrators])
            calibrator_lst.append(cal_info[:, 0].tolist())
            order_lst.append(cal_info[:, 1].tolist())
            tag_lst.append(cal_info[:, 2].tolist())
    return target_lst, calibrator_lst, order_lst, tag_lst


def create_OBs_from_lists(sci_lst, cal_lst, order_lst, tag_lst,
                          mode_selection: str, output_dir: Path,
                          array_config: str, res_dict: Dict,
                          standard_res: List) -> None:
    """"""
    for mode in OPERATIONAL_MODES[mode_selection]:
        print("-----------------------------")
        print(f"Making OBs for {mode}-mode")
        print("-----------------------------")
        if not tag_lst:
            tag_lst = copy_list_and_replace_all_values(cal_lst, "LN")
        if not order_lst:
            order_lst = copy_list_and_replace_all_values(cal_lst, "a")

        mode_out_dir = output_dir / mode
        if not mode_out_dir.exists():
            mode_out_dir.mkdir(parents=True, exist_ok=True)

        make_sci_obs(sci_lst, array_config, mode,
                     mode_out_dir, res_dict, standard_res)
        make_cal_obs(cal_lst, sci_lst, tag_lst, order_lst, array_config, mode,\
                     mode_out_dir, res_dict, standard_res)


def create_OBs_from_dict(mode_selection: str,
                         night_plan_data: Optional[Dict] = None,
                         night_plan_path: Optional[Path] = None,
                         output_dir: Optional[Path] = None,
                         res_dict: Optional[Dict] = {},
                         standard_res: Optional[List] = []) -> None:
    """This reads either the (.yaml)-file into a format suitable for the Jozsef
    Varga's OB creation code or reads out the run dict if 'run_data' is given,
    and subsequently makes the OBs.

    Also automatically gets the array_config from the run name and if not
    possible then prompts the user to input it

    Parameters
    ----------
    path2file: Path
        The night plan (.yaml)-file
    outpath: Path
        The output path
    mode_selection: str
        The mode MATISSE is operated in and for which the OBs are created.
        Either 'st' for standalone, 'gr' for GRA4MAT_ft_vis or 'both',
        if OBs for both are to be created
    res_dict: Dict, optional
        A dict with entries corresponding to non low-resolution
    standard_res: List, optional
        The default spectral resolutions for L- and N-band. By default it is set
        to medium for L- and low for N-band
    """
    if night_plan_data is not None:
        run_dict = night_plan_data
    elif night_plan_path is not None:
        with open(night_plan_path, "r") as night_plan_yaml:
            run_dict = yaml.safe_load(night_plan_yaml)
    else:
        raise IOError("Either the 'night_plan_data'- or the 'night_plan_path'-parameters"\
                      " must be given a value!")

    # TODO: Write down how the runs need to be written down in the observing plan -> Make
    # it automatic at some point
    for run_id, run in run_dict.items():
        print("-----------------------------")
        print(f"Making OBs for {run_id}...")
        logging.info(f"Creating OBs for '{run_id}'...")

        run_name = ''.join(run_id.split(",")[0].strip().split())
        run_dir = output_dir / run_name
        if not run_dir.exists():
            run_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Creating folder '{run_name}...'")

        array_config = get_array_config(run_id)
        write_run_prog_id(run_id, run_dir)

        for night_id, night in run.items():
            night_name = get_night_name_and_date(night_id)
            night_dir = run_dir / night_name
            if not night_dir.exists():
                night_dir.mkdir(parents=True, exist_ok=True)

            print("-----------------------------")
            print(f"Creating folder: '{night_dir.name}', and filling it with OBs")
            logging.info(f"Creating folder: '{night_dir.name}', and filling it with OBs")

            # NOTE: This avoids a timeout from the query-databases (such as Vizier)
            time.sleep(0.5)
            create_OBs_from_lists(*read_dict_to_lists(night), mode_selection,
                                  night_dir, array_config, res_dict, standard_res)


def ob_creation(output_dir: Path,
                sub_folder: Optional[Path] = None,
                night_plan_data: Optional[Dict] = None,
                night_plan_path: Optional[Path] = None,
                manual_lst: Optional[List] = [],
                res_dict: Optional[Dict] = {},
                standard_res: Optional[List] = None,
                mode_selection: str = "st",
                clean_previous: bool = False) -> None:
    """Gets either information from a 'nigh_plan.yaml'-file or a dictionary contain the
    run's data. Then it checks a dictionary for the resolution input for specific science
    targets and generates the OBS. Uses a standard resolution if none is provided.

    Parameters
    ----------
    output_dir: Path
    sub_folder: Path, optional
        A sub-folder in which the scripts are made into (if manually given)
    night_plan_data: Dict, optional
        The data that would be saved to a 'night_plan.yaml'-file
    night_plan_path: Path, optional
        The path to a 'night_plan.yaml'-file
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
    clean_previous: bool
        If toggled will remove the path given/in which the OBs are to be created
        DISCLAIMER: Danger this will remove all subfolders and data contined in it
    """
    output_dir = Path(output_dir, "manualOBs")\
            if manual_lst else Path(output_dir, "automaticOBs")

    if manual_lst:
        if sub_folder is not None:
            output_dir /= sub_folder
        array_config = get_array_config()
        try:
            sci_lst, cal_lst, tag_lst, order_lst = manual_lst
        except ValueError:
            raise ValueError("In case of manual input the four lists must be given!")
        create_OBs_from_lists(sci_lst, cal_lst, tag_lst, order_lst,
                              mode_selection, output_dir, array_config,
                              res_dict, standard_res)

    elif night_plan_path or night_plan_data:
        create_OBs_from_dict(mode_selection, night_plan_data, night_plan_path,
                             output_dir, res_dict, standard_res)
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
    path2file = "night_plan.yaml"
    outdir = Path("/Users/scheuck/Data/observations/obs/")

    sci_lst = []
    cal_lst = []
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
                res_dict=res_dict, mode_selection="both",
                standard_res="LOW", clean_previous=True)

