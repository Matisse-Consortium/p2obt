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
    * create_remote_folder - Creates a folder on P2 and returns its ID
    * get_subfolders - Gets all the folders from a directory
    * remote_folder_exists - Checks if a folder with that ID already exists on P2
    * generate_finding_chart_verify - Not yet implemented
    * make_folders_and_upload - Makes the individual folders for the OBs and uses the
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

    >>> ob_uploader(path, "production", ESO_USERNAME, ESO_PASSWORD)
"""
import os
import p2api
import warnings

from pathlib import Path
from typing import List, Optional

import loadobx

# TODO: Make readme template and add additional per night, then upload it
# FIXME: Make generateFindingCharts work and verification as well
# TODO: Add complete hour count for folders that have been made
# -> FIXME: Need fix of folder creation first
# BUG: Folder sorting sometimes doesn't work? -> Check if that persists?


README_TEMPLATE = ...


def remote_folder_exists(p2: p2api, container_id: int) -> bool:
    """Checks if the container with this id exists on P2

    Parameters
    ----------
    p2: p2api
        The p2ui python api
    container_id: int
        The id of the container on the P2

    Returns
    -------
    bool
        True or False if container exists on P2 or not
    """
    try:
        if p2.getContainer(container_id):
            return True
    except p2api.p2api.P2Error:
        pass

    return False


def get_corresponding_run(p2: p2api, period: str,
                          proposal_tag: str, number: int) -> int | None:
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
    run_id: int | None
        The run's Id that can be used to access and modify it with the p2api. If not found
        then None
    """
    runs = p2.getRuns()
    for run in runs[0]:
        run_period, run_proposal, run_number = run["progId"].split(".")
        run_number = int(run_number)

        if (run_period == period) and (run_proposal == proposal_tag) \
           and (run_number == number):
            return run["containerId"]
    return None


def create_remote_folder(p2: p2api, name: str, container_id: int) -> int:
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
    print(f"folder: {name} created!")
    return folder["containerId"]


# TODO: This function is not used right now  make it into iterative over subfolders
def get_subfolders(path: Path) -> List[str]:
    """Fetches the subfolders of a directory

    Parameters
    ----------
    path: Path
        The path of the folder of which the subfolders are to be fetched

    Returns
    -------
    List[str]
        List of the folders' paths
    """
    return [path / directory for directory in path.iterdir() if (path / directory).isdir()]


def update_readme():
    ...


def generate_charts_and_verify(p2: p2api, container_id: int) -> None:
    """Generates the finding charts and then verifies all OBs in the container

    p2: p2api
        The p2ui python api
    container_id: int
        The id of the container on the P2
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


def make_folders_for_obs(p2: p2api, obx_files: List[Path], container_id: int) -> None:
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
    # TODO: This can be simplified by a lot
    for i in obx_files:
        stem = "_".join(os.path.basename(i).split(".")[0].split("_"))
        if "SCI" in stem:
            sci_name = " ".join([j for j in stem.split("_")[1:]])
            folder_id = create_remote_folder(p2, sci_name, container_id)

            loadobx.loadob(p2, i, folder_id)

            for j in obx_files:
                stem_search = os.path.basename(j).split(".")[0]

                if "CAL" in stem_search:
                    sci_for_cal_name = " ".join(stem_search.split("_")[2:-1])
                    if sci_name == sci_for_cal_name:
                        loadobx.loadob(p2, j, folder_id)


def make_folders_and_upload(p2: p2api, upload_directories: List[Path], run_data: List):
    """This checks if run is specified or given by the folder names and then
    makes the same folders on the P2 and additional folders (e.g., for the
    'main_targets' and 'backup_targets' as well as for all the SCI-OBs. It then
    uploads the SCI- and CAL-OBs to the P2 as well

    Parameters
    ----------
    p2: p2api
        The P2 python api
    upload_directories: List[Path]
        List containing folders for upload
    run_data: List
        The data that is used to get the runId. The input needs to be in the
        form of a list [run_period: str, run_proposal: str, run_number: int].
        If the list does not contain the run_number, the script looks through
        the folders and fetches it automatically (e.g., run1, ...)
    """
    # TODO: Check if the run-id can be 0? If yes, make different error
    if len(run_data) == 3:
        run_id = get_corresponding_run(p2, *run_data)
        if run_id == 0:
            raise ValueError("Run could not be found!")

    # TODO: Make this more modular -> Recursive search for folders until it hits a
    # (.fits)-file
    night_folder_id_dict, main_folder_id_dict = {}, {}
    for directory in upload_directories:
        run_directories = directory.glob("*")
        run_directories.sort(key=lambda x: x[-3:])

        for run_directory in run_directories:
            if len(run_data) < 3:
                run_number = int(''.join([i for i in run_directory.name\
                                          if i.isdigit()]))
                run_id = get_corresponding_run(p2, *run_data, run_number)
                warnings.warn(f"Run: {run_directory} has not been found in p2ui! SKIPPED!")

            print(f"Making folders and uploading OBs to run {run_number}"\
                  f" with container id: {run_id}")

            night_directories = run_directory.glob("*")
            night_directories.sort(key=lambda x: x.name[:6])

            for night_directory in night_directories:
                night_name = night_directory.name

                if night_name not in night_folder_id_dict:
                    night_folder_id_dict[night_name] = create_remote_folder(p2, night_name, run_id)
                    main_folder_id_dict[night_name] = create_remote_folder(p2, "main_targets",
                                               night_folder_id_dict[night_name])
                    # TODO: Implement this
                    # backup_folder = create_remote_folder(p2, "backup_targets",
                                                  # night_folder_id_dict[night_name])

                mode_folder_id = create_remote_folder(p2, directory.name,
                                                      main_folder_id_dict[night_name])

                obx_files = night_directory.glob("*.obx")
                obx_files.sort(key=lambda x: x.name.split(".")[0][-2:])

                make_folders_for_obs(p2, obx_files, mode_folder_id)

                # TODO: Check function
                # generate_charts_and_verify(p2, mode_folder_id)
                # print(f"Container: {os.path.basename(i)} of {night_name} verified!")


def ob_uploader(root_dir: Path, run_data: List,
                server: Optional[str] = "production",
                username: Optional[str] = None):
    """Creates folders on the P2 and subsequently uploades the OBs

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
        The username for the P2
    """
    # TODO: Make manual entry for run data possible (full_night), maybe ask for
    # prompt for run number and night name
    p2 = loadobx.login(username, password, server)
    sub_directories = Path(root_dir).glob("*")

    if not sub_directories:
        raise FileNotFoundError("Either input path or folder structure is wrong. No files"
                                " could be found!")

    # TODO: Implement if there is also a standalone setting, that the same
    # nights are used for the standalone as well

    make_folders_and_upload(p2, sub_directories, run_data)
    print("Uploading done!")


if __name__ == "__main__":
    path = "/Users/scheuck/data/observations/obs"
    run_data = ["109", "2313"]
    ob_uploader(path, "production", run_data, "MbS")

