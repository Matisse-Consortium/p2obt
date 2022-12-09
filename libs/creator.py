#!/usr/bin/env python3

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
import sys
import yaml
import time
import logging

from glob import glob
from pathlib import Path
from warnings import warn
from types import SimpleNamespace
from typing import Dict, List, Optional

try:
    module = os.path.dirname(__file__)
    sys.path.append(module)
    # raise ValueError(file)
    import MATISSE_create_OB_2 as ob
except ImportError:
    raise ImportError("'MATISSE_create_OB_2.py'-file must be manually included in the 'lib/'")

# TODO: Make this work for N-band as well
# FIXME: Check back with Jozsef and or how to act if H_mag error occurs, or
# other script related errors

# TODO: Implement standard resolution

# FIXME: Two folders are created if SCI OB exists twice, remove that by making
# a set or something in automated OB creation

# TODO: Make sorting that automatically sorts the CALs and SCI in a correct way

if os.path.exists("logs/creator.log"):
    os.system("rm -rf logs/creator.log")
else:
    os.mkdir("logs")
logging.basicConfig(filename='logs/creator.log', filemode='w',
                    format='%(asctime)s - %(message)s', level=logging.INFO)

# Dicts for the template and resolution configuration
UT_DICT_STANDALONE = {"ACQ": ob.acq_tpl,
                      "LOW": {"TEMP": [ob.obs_tpl], "DIT": [0.111],
                              "RES": ["L-LR_N-LR"]}}

AT_DICT_GRA4MAT = {"ACQ": ob.acq_ft_tpl,
                   "LOW": {"TEMP": [ob.obs_ft_tpl], "DIT": [1.], "RES":
                           ["L-LR_N-LR"]},
                   "MED": {"TEMP": [ob.obs_ft_tpl],
                           "DIT": [1.3], "RES": ["L-MR_N-LR"]},
                   "HIGH": {"TEMP": [ob.obs_ft_tpl],
                           "DIT": [3.], "RES": ["L-HR_N-LR"]}}

UT_DICT_GRA4MAT = {"ACQ": ob.acq_ft_tpl,
                   "LOW": {"TEMP": [ob.obs_ft_vis_tpl], "DIT": [0.111], "RES":
                           ["L-LR_N-LR"]},
                   "MED": {"TEMP": [ob.obs_ft_coh_tpl, ob.obs_ft_vis_tpl],
                           "DIT": [1.3, 0.111], "RES": ["L-MR_N-LR"]},
                   "HIGH": {"TEMP": [ob.obs_ft_coh_tpl, ob.obs_ft_vis_tpl],
                           "DIT": [3., 0.111], "RES": ["L-HR_N-LR"]}}

TEMPLATE_RES_DICT = {"standalone": {"UTs": UT_DICT_STANDALONE},
                     "GRA4MAT_ft_vis": {"UTs": UT_DICT_GRA4MAT,
                                        "ATs": AT_DICT_GRA4MAT}}

AT_CONFIG = ["small", "medium", "large"]
TEL_CONFIG = ["UTs", *AT_CONFIG]


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

    if len(night.split()) > 2:
        night, date = night.split(",")[:2]

    return "_".join([''.join(night.split()), ''.join(date.split())])\
            if date != '' else ''.join(night.split())


def get_array_config(run_name: Optional[str] = "") -> str:
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
                             " ('UTs': 1; 'small': 2, 'medium': 3, 'large: 4): "))-1
            return TEL_CONFIG[user_inp]
    else:
        user_inp = int(input("No configuration can be found, please input"\
                         " ('UTs': 1; 'small': 2, 'medium': 3, 'large: 4): "))-1
        return TEL_CONFIG[user_inp]


def make_sci_obs(targets: List, array_config: str,
                 mode: str, output_dir: str, res_dict: Dict,
                 standard_resolution: List, upload_prep: Optional[bool] = False) -> None:
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
    upload_prep: bool, optional
        If toggled will rename the (.obx)-files so that they are uploaded in the right
        order
    """
    array_key = "UTs" if array_config == "UTs" else "ATs"
    template = TEMPLATE_RES_DICT[mode][array_key]
    ACQ = template["ACQ"]

    if not standard_resolution:
        standard_resolution = "LOW" if array_config == "UTs" else "MED"

    for index, target in enumerate(targets):
        try:
            if res_dict and (target in res_dict):
                temp = SimpleNamespace(**template[res_dict[target]])
            else:
                temp = SimpleNamespace(**template[standard_resolution])

            ob.mat_gen_ob(target, array_config, 'SCI', outdir=output_dir,\
                          spectral_setups=temp.RES, obs_tpls=temp.TEMP,\
                          acq_tpl=ACQ, DITs=temp.DIT)

            # NOTE: Renames the file created to account for order while globbing for upload
            if upload_prep:
                files = glob(os.path.join(output_dir, "*.obx"))
                latest_file = max(files, key=os.path.getctime)
                latest_file_new_name = os.path.basename(latest_file).split(".")[0]\
                        + f"_{index}.obx"
                latest_file_new_name = os.path.join(os.path.dirname(latest_file),
                                                    latest_file_new_name)
                os.rename(latest_file, latest_file_new_name)
                logging.info(f"Created OB SCI-{latest_file_new_name}")
            else:
                logging.info(f"Created OB SCI-{target}")

        except Exception:
            logging.error("Skipped - OB", exc_info=True)
            print("ERROR: Skipped OB - Check (.log)-file!")


def make_cal_obs(calibrators: List, targets: List, tags: List,
                 array_config: str, mode: str, output_dir: Path,
                 resolution_dict: Optional[Dict] = {},
                 standard_resolution: Optional[List] = [],
                 upload_prep: Optional[bool] = False) -> None:
    """Checks if there are sublists in the calibration list and calls the 'mat_gen_ob' with the right inputs
    to generate the calibration objects.
    The input lists correspond to each other index-wise (e.g., cal_lst[1], sci_lst[1], tag_lst[1]; etc.)

    Parameters
    ----------
    calibrators: List
        Contains the calibration objects corresponding to the science objects
    targets: List
        Contains the science objects
    tags: List
        Contains the tags (either 'L', 'N', or both) and corresponds to the science objects
    array_config: str
        The array configuration ('small', 'medium', 'large') or 'UTs'
    mode: str
        The mode of operation of MATISSE
    output_dir: Path
        The output directory, where the '.obx'-files will be created in
    resolution_dict: Dict, optional
    standard_res: List, optional
        The default spectral resolutions for l- and n-band. set to LOW for the UTs
        and to MED for the ATs as a default
    """
    array_key = "UTs" if array_config == "UTs" else "ATs"
    template = TEMPLATE_RES_DICT[mode][array_key]
    ACQ = template["ACQ"]

    if not standard_resolution:
        standard_resolution = "LOW" if array_config == "UTs" else "MED"

    # NOTE: Iterates through the calibration list
    for list_index, calibrator in enumerate(calibrators):
        try:
            if resolution_dict and (targets[list_index] in resolution_dict):
                calibrator_template = SimpleNamespace(**template[resolution_dict[targets[list_index]]])
            else:
                calibrator_template = SimpleNamespace(**template[standard_resolution])

            # NOTE: Checks if list item is itself a list
            if isinstance(calibrator, list):
                for nested_list_index, single_calibrator in enumerate(calibrator):
                    ob.mat_gen_ob(single_calibrator, array_config, 'CAL', outdir=output_dir,
                                  spectral_setups=calibrator_template.RES,
                                  obs_tpls=calibrator_template.TEMP,
                                  acq_tpl=ACQ, sci_name=targets[list_index],
                                  tag=tags[list_index][nested_list_index],
                                  DITs=calibrator_template.DIT)
            else:
                ob.mat_gen_ob(calibrator, array_config, 'CAL', outdir=output_dir,
                              spectral_setups=calibrator_template.RES,
                              obs_tpls=calibrator_template.TEMP,
                              acq_tpl=ACQ, sci_name=targets[list_index],
                              tag=tags[list_index], DITs=calibrator_template.DIT)

            # TODO: Maybe also add list index here for upload and sorting, list index of
            # target plus 0 or 1 for before or after?
            logging.info(f"Created OB CAL-#{list_index}")

        except Exception:
            logging.error("Skipped - OB", exc_info=True)
            print("ERROR: Skipped OB - Check (.log)-file")


def read_dict_into_OBs(mode: str,
                       night_plan_path: Optional[Path] = "",
                       output_dir: Optional[Path] = "",
                       run_data: Optional[Dict] = {},
                       res_dict: Optional[Dict] = {},
                       standard_res: Optional[List] = [],
                       upload_prep: Optional[bool] = False) -> None:
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
    mode: str
        The mode of operation of MATISSE
    res_dict: Dict, optional
        A dict with entries corresponding to non low-resolution
    standard_res: List, optional
        The default spectral resolutions for L- and N-band. By default it is set
        to medium for L- and low for N-band
    upload_prep: bool, optional
        If toggled will rename the (.obx)-files so that they are uploaded in the right
        order
    """
    if run_data:
        run_dict = run_data
    elif night_plan_path:
        with open(night_plan_path, "r") as fy:
            run_dict = yaml.safe_load(fy)
    else:
        raise IOError("Either the 'run_data'- or the 'night_plan_path'-parameters"\
                      " must be given a value!")

    for run_name, run_content in run_dict.items():
        print(f"Making OBs for {run_name}")
        # TODO: Add spacing for logging
        logging.info(f"Creating OBs for '{run_name}'")
        array_config = get_array_config(run_name)
        run_name = ''.join(run_name.split(",")[0].strip().split())
        logging.info(f"Creating folder: '{run_name}'")

        for night_name, night_content in run_content.items():
            night_name = get_night_name_and_date(night_name)

            night_path = os.path.join(output_dir, run_name, night_name)
            if not os.path.exists(night_path):
                os.makedirs(night_path)

            print(f"Creating folder: '{night_name}', and filling it with OBs")
            logging.info(f"Creating folder: '{night_name}', and filling it with OBs")

            # NOTE: This avoids a timeout from the query-databases
            time.sleep(0.5)

            night = SimpleNamespace(**night_content)
            make_sci_obs(night.SCI, array_config, mode,
                         night_path, res_dict, standard_res, upload_prep)
            make_cal_obs(night.CAL, night.SCI, night.TAG, array_config,
                         mode, night_path, res_dict, standard_res, upload_prep)


def ob_creation(output_dir: Path,
                night_plan_path: Optional[Path] = "",
                manual_lst: Optional[List] = [],
                run_data: Optional[Dict] = {},
                res_dict: Optional[Dict] = {},
                standard_res: Optional[List] = [],
                mode: str = "st",
                upload_prep: Optional[bool] = False) -> None:
    """Gets either information from a 'nigh_plan.yaml'-file or a dictionary contain the
    run's data. Then it checks a dictionary for the resolution input for specific science
    targets and generates the OBS. Uses a standard resolution if none is provided.

    Parameters
    ----------
    array_config: str
        The array configuration
    night_plan_path: Path, optional
        The path to the 'night_plan.yaml'-file
    manual_lst: List, optional
        The manual input of [targets, calibrators, tags]
    run_data: Dict, optional
    resolution_dict: Dict, optional
        A dict with entries corresponding the resolution
    standard_res: List, optional
        The default spectral resolutions for L- and N-band. By default it is set
        to medium for L- and low for N-band
    mode: str
        The mode MATISSE is operated in and for which the OBs are created.
        Either 'st' for standalone, 'gr' for GRA4MAT_ft_vis or 'both',
        if OBs for both are to be created
    upload_prep: bool, optional
        If toggled will rename the (.obx)-files so that they are uploaded in the right
        order
    """
    modes = ["standalone", "GRA4MAT_ft_vis"] if mode == "both" else \
            (["standalone"] if mode == "st" else ["GRA4MAT_ft_vis"])

    for mode in modes:
        if manual_lst:
            sci_lst, cal_lst, tag_lst = manual_lst
            if not tag_lst:
                tag_lst = ["LN"]*len(cal_lst)
                warn("The 'tag_lst' has been set to 'LN' for all targets!")

            output_dir = os.path.join(output_dir, "manualOBs")

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            array_config = get_array_config()
            make_sci_obs(sci_lst, array_config, mode, output_dir, res_dict,
                         standard_res, upload_prep=upload_prep)
            make_cal_obs(cal_lst, sci_lst, tag_lst, array_config, mode,\
                         output_dir, res_dict, standard_res)

        elif night_plan_path or run_data:
            read_dict_into_OBs(mode, night_plan_path, os.path.join(output_dir, mode),
                               run_data, res_dict, standard_res)

        else:
            raise IOError("Neither '.yaml'-file nor input list found or input"
                          " dict found!")


if __name__ == "__main__":
    path2file = "night_plan.yaml"
    outdir = "/Users/scheuck/Data/observations/obs/"

    sci_lst = ["DR Tau"]
    cal_lst = ["HD 33554"]
    tag_lst = []
    manual_lst = [sci_lst, cal_lst, tag_lst]

    res_dict = {}

    ob_creation(outdir, manual_lst=manual_lst,
                res_dict=res_dict, mode="st", standard_res="LOW")

