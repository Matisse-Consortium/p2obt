"""OB Uploader

This script makes the main folders for a MATISSE run in P2, i.e., the nights in
which are observed, the mode in which is observed (GRA4MAT or standalone) and
the subfolders 'main_targets' and 'backup_targets'. Additionally, under the
'main_targets'-folder it creates a folder for every SCI-OB, and imports the
SCI-OB as well as the corresponding CALs into the folder.

DISCLAIMER: Guaranteed for working only in conjunction with the 'parseOBplan'
and the 'automaticOBcreation' scripts, as they format the folders correctly.

The structure that the folder of the given path need to be in is the following:
    >>> path/<GRA4MAT_ft_vis or standalone>/<run>/<night>/*.obx

This is automatically the case if the folders are made with the above mentioned
scripts.

This file can also be imported as a module and contains the following functions:
    * get_corresponding_run - Gets a run corresponding to an input List
    * create_folder - Creates a folder on P2 and returns its ID
    * get_subfolders - Gets all the folders from a directory
    * check4folder - Checks if a folder with that ID already exists
    * generate_finding_chart_verify - Not yet implemented
    * make_folders4OBs - Makes the individual folders for the OBs and uses the
    'loadobx' script to import the already made (.obx)-files to P2
    * ob_uploader - The main loop of the script, makes the folders and uploads
    the OBs in a folder to the P2

Example of usage:
    >>> from uploader import ob_uploader

    # The path to the top most folder

    >>> path = "/Users/scheuck/Documents/PhD/matisse_stuff/observation/phase2/obs"

    # The data describing the run

    >>> run_data = ["109", "2313"]

    # The main loop

    >>> ob_uploader(path, "production", run_data, "MbS", "QekutafAmeNGNVZ")
"""
import os
import p2api
import warnings

from glob import glob
from pathlib import Path
from typing import List, Optional

import loadobx

# TODO: Make readme template and add additional per night, then upload it
# FIXME: Make generateFindingCharts work and verification as well
# TODO: Add complete hour count for folders that have been made
# -> FIXME: Need fix of folder creation first
# BUG: Folder sorting sometimes doesn't work? -> Check if that persists?

README_TEMPLATE = ...


def _get_corresponding_run(p2, period: str, proposal_tag: str, number: int) -> int:
    """Gets the run that corresponds to the period, proposal and the number and
    returns its runId

    Parameters
    ----------
    p2: p2api
        The p2ui python api
    period: str
        The period the run is part of
    proposal_tag: str
        The proposal the run is part of, specifically the tag that is in the
        run's name
    number: int
        The number of the run

    Returns
    -------
    run_id: int
        The run's Id that can be used to access and modify it with the p2api
    """
    runs = p2.getRuns()
    for run in runs[0]:
        run_period, run_proposal, run_number = run["progId"].split(".")
        run_number = int(run_number)

        if (run_period == period) and (run_proposal == proposal_tag) \
           and (run_number == number):
            return run["containerId"]
    return 0


def _create_folder(p2, name: str, container_id: int) -> int:
    """Creates a folder in either the run or the specified directory

    Parameters
    ----------
    p2: p2api
        The P2 python api
    name: str
        The folder's name
    container_id: int
        The id that specifies the run

    Returns
    -------
    folder_id: int
    """
    folder, _ = p2.createFolder(container_id, name)
    folder_id = folder["containerId"]
    print(f"folder: {name} created!")
    return folder_id


def _get_subfolders(root_dir: Path) -> List:
    """Fetches the subfolders of a directory

    Parameters
    ----------
    root_dir: Path
        The path of the folder of which the subfolders are to be fetched

    Returns
    -------
    List
        List of the folder-paths
    """
    return [os.path.join(root_dir, directory) for directory in os.listdir(root_dir)\
            if os.path.isdir(os.path.join(root_dir, directory))]


def folder_exists(p2, container_id: int) -> bool:
    """Checks if the container with this id exists on P2

    Parameters
    ----------
        The id of the container on the P2

    Returns
    -------
    bool
        True or False if container exists on P2 or not
    """
    if container_id is None:
        return False

    try:
        if p2.getContainer(container_id):
            return True
    except p2api.p2api.P2Error:
        return False


# TODO: Implement this function -> Maybe rename
def update_readme():
    ...


def generate_charts_and_verify(p2, container_id: int):
    """Generates the finding charts and then verifies all OBs in the container

    p2: p2api
    container_id: int
    """
    folders = p2.getItems(container_id)

    for folder in folders[0]:
        obx_files = p2.getItems(folder["containerId"])

        for obx_file in obx_files[0]:
            p2.generateFindingChart(obx_file["obId"])
            print(f"Finding chart created for OB {obx_file['name']}!")

            p2.verifyOB(obx_file["obId"])
            print(f"OB {obx_file['name']} verified!")

    p2.verifyContainer(container_id, True)


def make_folder_and_place_obs(p2, files: List[Path], container_id: int) -> None:
    """Makes the respective folders for a list of (.obx)-files

    Parameters
    ----------
    p2: p2api
        The P2 python api
    files: List[Path]
        The (.obx)-files from the lowest folder in the directory
    container_id: int
        The id of the container on the P2
    """
    for file in files:
        stem = "_".join(os.path.basename(file).split(".")[0].split("_")[:-1])
        if "SCI" in stem:
            sci_name = " ".join([j for j in stem.split("_")[1:]])
            folder_id = _create_folder(p2, sci_name, container_id)

            loadobx.loadob(p2, file, folder_id)

            for j in files:
                stem_search = os.path.basename(j).split(".")[0]

                if "CAL" in stem_search:
                    sci4cal_name = " ".join(stem_search.split("_")[2:-1])
                    if sci_name == sci4cal_name:
                        loadobx.loadob(p2, j, folder_id)


def make_folders_and_upload(p2, top_dir: List, run_data: List):
    """This checks if run is specified or given by the folder names and then
    makes the same folders on the P2 and additional folders (e.g., for the
    'main_targets' and 'backup_targets' as well as for all the SCI-OBs. It then
    uploads the SCI- and CAL-OBs to the P2 as well

    Parameters
    ----------
    p2: p2api
    top_dir: List
        List containing either 'GRA4MAT_ft_vis'-, 'standalone'-folder or both
    run_data: List
        The data that is used to get the runId. The input needs to be in the
        form of a list [run_period: str, run_proposal: str, run_number: int].
        If the list does not contain the run_number, the script looks through
        the folders and fetches it automatically (e.g., run1, ...)
    """
    # TODO: Check if the run-id can be 0? If yes, make different error
    if len(run_data) == 3:
        run_id = _get_corresponding_run(p2, *run_data)
        if run_id == 0:
            raise ValueError("No run found!")

    night_folder_id_dict, main_folder_id_dict = {}, {}
    for i in top_dir:
        runs = glob(os.path.join(i, "*"))
        runs.sort(key=lambda x: x[-3:])

        for j in runs:
            if len(run_data) < 3:
                run_number = int(''.join([i for i in os.path.basename(j)\
                                          if i.isdigit()]))
                run_id = _get_corresponding_run(p2, *run_data, run_number)
                warnings.warn(f"Run: {j} has not been found in p2ui! SKIPPED!")

            print(f"Making folders and uploading OBs to run {run_number}"\
                  f" with container id: {run_id}")

            nights = glob(os.path.join(j, "*"))
            nights.sort(key=lambda x: os.path.basename(x)[:6])

            for k in nights:
                night_name = os.path.basename(k)

                if night_name not in night_folder_id_dict:
                    night_folder_id_dict[night_name] = _create_folder(p2, night_name, run_id)
                    main_folder_id_dict[night_name] = _create_folder(p2, "main_targets",
                                               night_folder_id_dict[night_name])
                    backup_folder = _create_folder(p2, "backup_targets",
                                                  night_folder_id_dict[night_name])

                mode_folder_id = _create_folder(p2, os.path.basename(i),
                                               main_folder_id_dict[night_name])

                obx_files = glob(os.path.join(k, "*.obx"))
                obx_files.sort(key=lambda x: os.path.basename(x).split(".")[0][-2:])

                make_folder_and_place_obs(p2, obx_files, mode_folder_id)

                # TODO: Implement this functionality
                # generate_charts_and_verify(p2, mode_folder_id)
                # print(f"Container: {os.path.basename(i)} of {night_name} verified!")


def ob_uploader(root_path: Path, run_data: List,
                server: Optional[str] = "production",
                username: Optional[str] = ""):
    """Creates folders on the p2ui and subsequently uploades the OBs to the P2

    Parameters
    ----------
    path: Path
        The path to the top most folder (containing GRA4MAT_ft_vis or
        standalone)
    run_data: List
        The data that is used to get the runId. The input needs to be in the
        form of a list [run_period: str, run_proposal: str, run_number: int].
        If the list does not contain the run_number, the script looks through
        the folders and fetches it automatically (e.g., run1, ...)
    server: str
        The enviroment to which the (.obx)-file is uploaded, 'demo' for testing,
        'production' for paranal and 'production_lasilla' for la silla
    username: str, optional
        The username for the p2ui
    password: str, optional
        The password for the p2ui
    """
    # TODO: Make manual entry for run data possible (full_night), maybe ask for
    # prompt for run number and night name
    p2 = loadobx.login(username, password, server)
    top_dir = glob(os.path.join(root_path, "*"))

    if not top_dir:
        raise IOError("Either input path or folder structure is wrong. No files"
                      " could be found!")

    # TODO: Implement if there is also a standalone setting, that the same
    # nights are used for the standalone as well
    make_folders_and_upload(p2, top_dir, run_data)
    print("Uploading done!")


if __name__ == "__main__":
    _get_subfolders("")

