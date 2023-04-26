"""OB Uploader

This script makes the main folders for a MATISSE run in P2, i.e., the nights in
which are observed, the mode in which is observed (GRA4MAT or standalone) and
the subfolders 'main_targets' and 'backup_targets'. Additionally, under the
'main_targets'-folder it creates a folder for every SCI-OB, and imports the
SCI-OB as well as the corresponding CALs into the folder.

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
import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml

import p2api
import loadobx

# FIXME: Cleanup with new startup, or describe folder that needs to uploaded
# TODO: Make readme template and add additional per night, then upload it
# FIXME: Make generateFindingCharts work and verification as well
# TODO: Add complete hour count for folders that have been made
# FIXME: Need fix of folder creation first
# BUG: Folder sorting sometimes doesn't work? -> Check if that persists?

LOG_PATH = Path(__file__).parent / "logs/uploader.log"

if LOG_PATH.exists():
    os.remove(LOG_PATH)
else:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.touch()

logging.basicConfig(filename=LOG_PATH, filemode='w',
                    format='%(asctime)s - %(message)s', level=logging.INFO)

# TODO: Hard code this and check for upload
README_TEMPLATE = {"Date": "", "Main observer": "",
                   "e-mail": "", "Phone number": "",
                   "Skype": "", "Zoom": ""}


def get_remote_run(p2_connection: p2api, run_id: str) -> int | None:
    """Gets the run that corresponds to the period, proposal and the number and
    returns its runId

    Parameters
    ----------
    p2_connection: p2api
        The p2ui python api
    run_id: str
        The run's id in the format (period.proposal_tag.run_number)

    Returns
    -------
    run_id: int | None
        The run's Id that can be used to access and modify it with the p2api. If not found
        then None
    """
    for run in p2_connection.getRuns()[0]:
        if run_id == run["progId"]:
            return run["containerId"]
    return None


def remote_container_exists(p2_connection: p2api, container_id: int) -> bool:
    """Checks if the container with this id exists on P2

    Parameters
    ----------
    p2_connection: p2api
        The p2ui python api
    container_id: int
        The id of the container (either run or folder) on the P2

    Returns
    -------
    container_exists: bool
        'True' if container exists, otherwise 'False'
    """
    try:
        if p2_connection.getContainer(container_id):
            return True
    except p2api.p2api.P2Error:
        return False


def create_remote_container(p2_connection: p2api,
                            name: str, container_id: int,
                            observation_mode: Optional[str] = "visitor") -> int:
    """Creates a container (either a run or folder) on P2

    Parameters
    ----------
    p2_connection: p2api
        The P2 python api
    name: str
        The folder's name
    container_id: int
        The id that specifies the container (a run or folder on P2)
    observation_mode: str
        Can either be "visitor" for Visitor Mode (VM) or "service" for Service Mode (SM)

    Returns
    -------
    container_id: int
        The created container's id
    """
    print(f"Creating container {name}")
    if observation_mode == "visitor":
        container, _ = p2_connection.createFolder(container_id, name)
    elif observation_mode == "service":
        container, _ = p2_connection.createConcatenation(container_id, name)
    else:
        raise IOError("No such operation mode exists!")
    return container["containerId"]


def update_readme():
    ...


# TODO: This function is not used right now  make it into iterative over subfolders
# TODO: Make the upload ask for the run-id if it cannot be determined
def get_subfolders_containing_files(search_directory: Path,
                                    file_type: Optional[str] = ".obx") -> List[Path]:
    """Recursively searches through the whole subtree of the search directory and returns
    the folders containt the specified filetype as a list of paths

    Parameters
    ----------
    search_path: Path
        The path of the folder of which the subfolders are to be fetched
    file_type: str, optional
        The filetype that is being searched for

    Returns
    -------
    List[Path]
        List of the folders' paths
    """
    directories_with_obx_files = []

    for child in search_directory.rglob(f"*{file_type}"):
        parent_directory = child.parent

        if parent_directory not in directories_with_obx_files:
            directories_with_obx_files.append(parent_directory)

    return [directory.relative_to(search_directory)\
            for directory in directories_with_obx_files]


def sort_science_and_calibrator(science_to_calibrator_dict: Dict) -> Dict:
    """This checks if the science targets or calibrators are made in a sortable way and if
    not just returns the dict, otherwise it sorts them by their appended digit

    Parameters
    -----------
    science_to_calibrator_dict: Dict
        A dictionary containing the "name" of the science target as key and as value a
        list of Paths with all its associated (.obx)-file paths

    Returns
    -------
    science_to_calibrator_dict: Dict
    """
    for science_target, obx_files in science_to_calibrator_dict.items():
        if any([obx_file.stem.endswith(("#a", "#b")) for obx_file in obx_files]):
            science_to_calibrator_dict[science_target] = \
                    sorted(obx_files, key=lambda x: (x.name.find("b") >= 0,
                                                     x.name.find("a") >= 0))
    return science_to_calibrator_dict


def pair_science_to_calibrators(upload_directory: Path, obx_folder: Path) -> Dict:
    """Pairs up the science targets and calibrators (.obx)-files into a dict

    Parameters
    ----------
    upload_directory: Path
    obx_folder: Path
        A folder containing (.obx)-files

    Returns
    -------
    sorted_science_and_calibrator_dict: Dict
    """
    science_to_calibrator_dict = {}
    obx_files = (upload_directory / obx_folder).glob("*.obx")
    obx_files = sorted(obx_files, key=lambda x: x.stem.split("#")[1])

    for obx_file in obx_files:
        stem = obx_file.stem
        if "SCI" in stem:
            science_target_name = "_".join([part for part\
                                            in stem.split("#")[0].split("_")[1:]])
            science_to_calibrator_dict[science_target_name] = [obx_file]
        else:
            science_target_of_calibrator = "_".join(stem.split("_")[2:-1])
            science_to_calibrator_dict[science_target_of_calibrator].append(obx_file)

    return sort_science_and_calibrator(science_to_calibrator_dict)


def upload_obx_to_container(p2_connection: p2api, target: str,
                            obx_files: List[Path], container_id: int,
                            observation_mode) -> None:
    """Uploads (.obx)-files contained in a list to a given container

    Parameters
    ----------
    p2_connection: p2api
        The p2ui python api
    target: str
    obx_files: List[Path]
    container_id: int
    observation_mode: str, optional
    """
    print("--------------------------")
    obx_container_id = create_remote_container(p2_connection, target,
                                               container_id, observation_mode)

    for obx_file in obx_files:
        try:
            ob_id = loadobx.loadob(p2_connection, obx_file, obx_container_id)
            # print(f"\tCreating finding charts {obx_file}")
            # p2_connection.generateFindingChart(ob_id)
            # print(f"\tVerifying finding charts {obx_file}")
            # p2_connection.verifyOB(ob_id)
        except Exception:
            logging.error(f"Skipped OB-Upload: {obx_file}", exc_info=True)
            print(f"ERROR: Skipped OB-Upload: {obx_file.stem} -- Check 'uploader.log'-file")


# TODO: Make this upload funcitonality better -> Iteratively, but only upload the relevant
# names to the runs, such as night or the total run for Service Mode
def create_folder_structure_and_upload(p2_connection: p2api,
                                       upload_directory: Path,
                                       obx_folder: Path, run_id: int,
                                       container_ids: Dict, containers: set,
                                       observation_mode: str):
    """

    Parameters
    ----------
    p2_connection: p2api
    upload_directory: Path
    obx_folder: Path
    run_id: int
    container_ids: Dict
    containers: set
    observation_mode: str, optional
        Can either be "visitor" for Visitor Mode (VM) or "service" for Service Mode (SM)
    """
    # FIXME: Make container_id upload work
    container_id = 0

    # TODO: Sort folders in some way iteratively?

    if observation_mode == "visitor":
        for parent in obx_folder.parents[::-1][1:]:
            if parent in containers:
                continue

            if parent.parent != Path("."):
                if container_id == 0:
                    container_id = container_ids[parent.parent]

                container_id = create_remote_container(p2_connection, parent.name,
                                                       container_id)
                container_ids[parent] = container_id
            else:
                container_id = create_remote_container(p2_connection, parent.name,
                                                       run_id)
                container_ids[parent] = container_id
            containers.add(parent)

            if container_id == 0:
                # HACK: This is a botched fix for a weird bug that it only takes folders that
                # originated from same file??
                if container_ids:
                    container_id = container_ids[obx_folder.parent]
                else:
                    container_id = run_id

            container_id = create_remote_container(p2_connection, obx_folder.stem,
                                                   container_id)
    elif observation_mode == "service":
        container_id = run_id

    for target, obx_files in pair_science_to_calibrators(upload_directory, obx_folder).items():
        upload_obx_to_container(p2_connection, target,
                                obx_files, container_id, observation_mode)

    return container_ids, containers


# FIXME: This gets called quite often? Important to reduce the number of calls?
def get_run_prog_id(upload_directory: Path, folder: Path):
    """Gets the run's program id from the (.yaml)-file of the run or manual input"""
    base_directory = str(folder.parents[-2])
    run_prog_id = None
    if "run" in base_directory:
        yaml_file = upload_directory / base_directory / "run.yaml"
        with open(yaml_file, "r") as f:
            yaml_content = yaml.safe_load(f)
        if yaml_content is not None:
            return yaml_content["run_prog_id"]

    if run_prog_id is None:
        print("Run's id could not be automatically detected!")
        return input("Please enter the run's id in the following form"
                     " (<period>.<program>.<run> (e.g., 110.2474.004)): ")


def ob_uploader(upload_directory: Path,
                run_prog_id: Optional[str] = None,
                container_id: Optional[int] = None,
                server: Optional[str] = "production",
                observation_mode: Optional[str] = "visitor",
                username: Optional[str] = None,
                password: Optional[str] = None) -> None:
    """This checks if run is specified or given by the folder names and then
    makes the same folders on the P2 and additional folders (e.g., for the
    'main_targets' and 'backup_targets' as well as for all the SCI-OBs. It then
    uploads the SCI- and CAL-OBs to the P2 as well

    Parameters
    ----------
    upload_directories: List[Path]
        List containing folders for upload
    run_prog_id: str, optional
        The program id of the run. Used to fetch the run to be uploaded to
    container_id: int, optional
        If this is provided then only the subtrees of the upload_directory will be
        given container. This overrides the run_data input. This will upload to the
        specified container directly
    observation_mode: str, optional
        Can either be "visitor" for Visitor Mode (VM) or "service" for Service Mode (SM)
    server: str
        The enviroment to which the (.obx)-file is uploaded, 'demo' for testing,
        'production' for paranal and 'production_lasilla' for la silla
    username: str, optional
        The username for the P2
    password: str, optional
        The password for the P2
    """
    p2_connection = loadobx.login(username, password, server)

    # if container_id:
        # run_id = container_id
    # elif run_prog_id:
        # run_id = get_remote_run(p2_connection, run_prog_id)
    # else:
        # raise IOError("Either run-program-id or container-id must be given!")

    obx_folders = get_subfolders_containing_files(upload_directory)

    container_ids, containers = {}, set()
    for obx_folder in obx_folders:
        # NOTE: Skip this if the run_prog_id is given
        if run_prog_id is None:
            run_prog_id = get_run_prog_id(upload_directory, obx_folder)
            run_id = get_remote_run(p2_connection, run_prog_id)
        container_ids, containers =\
                create_folder_structure_and_upload(p2_connection, upload_directory,
                                                   obx_folder, run_id,
                                                   container_ids, containers,
                                                   observation_mode)


# TODO: Make container id also upload files to an empty folder directly
# TODO: Sort GRA4MAT to the top
# TODO: Make night sorting also
if __name__ == "__main__":
    path = Path("/Users/scheuck/data/observations/obs/automaticOBs/")
    ob_uploader(path, username="MbS", observation_mode="service")



#########
# New Stuff


# TODO: Think of way to immediately populate the templates and avoid unnecessary overhead
def _add_templates(p2_connection: p2api,
                   ob_id: int, templates: List[str]):
    """Adds templates to an OB

    Parameters
    ----------
    p2_connection: p2api
    ob_id: int
    templates: List[str]
    """
    for template in templates:
        content, id = p2api.createTemplate(ob_id, template)
    return