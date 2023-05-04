import logging
from pathlib import Path
from typing import Union, Optional, Any, Dict, List, Tuple

import numpy as np
import p2api

from .backend import options
from .backend.compose import set_ob_name, write_ob, compose_ob
from .backend.parse import parse_array_config, parse_operational_mode,\
    parse_run_resolution, parse_run_prog_id, parse_night_name, parse_night_plan
from .backend.upload import login, get_remote_run,\
    create_remote_container, upload_ob


# TODO: Make this shorter? Or into an option even?
OPERATIONAL_MODES = {"both": ["standalone", "GRA4MAT"],
                     "st": ["standalone"], "gr": ["GRA4MAT"],
                     "matisse": ["standalone"], "gra4mat": ["GRA4MAT"]}

# TOOD: Add night astronomer comments to template
# TODO: Find way to switch of photometry of template
def copy_list_and_replace_values(input_list: List[Any], value: Any) -> List:
    """Replaces all values in list with the given value. Takes into account
    nested lists.

    Parameters
    ----------
    input_list : list of any
        An input list of any form. May contain once-nested lists.
    value : any
        Any value that will make up the new list.

    Returns
    -------
    output_list : list
        The input_list with all its values replaced by the given value.
    """
    output_list = input_list.copy()
    for index, element in enumerate(input_list):
        if isinstance(element, list):
            for sub_index, _ in enumerate(element):
                output_list[index][sub_index] = value
        else:
            output_list[index] = value
    return output_list


def read_dict_to_lists(night: Dict) -> Tuple[List[Any]]:
    """Reads the data of the night plan contained in a dictionary
    into the four lists (targets, calibrators, order and tags)."""
    targets, calibrators, orders, tags = [], [], [], []
    for target, calibrator in night.items():
        targets.append(target)
        if len(calibrator) == 1:
            calibrators.append(calibrator[0]["name"])
            orders.append(calibrator[0]["order"])
            tags.append(calibrator[0]["tag"])
        else:
            cal_info = np.array([(calibrator["name"],
                                  calibrator["order"],
                                  calibrator["tag"])
                                for calibrator in calibrator])
            calibrators.append(cal_info[:, 0].tolist())
            orders.append(cal_info[:, 1].tolist())
            tags.append(cal_info[:, 2].tolist())
    return targets, calibrators, orders, tags


def unwrap_lists(target: str,
                 calibrator: Union[str, List[str]],
                 order: Union[str, List[str]],
                 tag: Union[str, List[str]]):
    """This untangles the calibrators, orders and tags
    lists into a sequential lists that has the target at
    its centre.

    The structure of the list is that they contain tuples
    as entries of the form (<calibrator/target>, <cal/sci-flag>, <tag>,).

    Parameters
    ----------

    Returns
    -------
    """
    calibrators_before, calibrators_after = [], []
    if isinstance(calibrator, list):
        for cal, ord, tg in zip(calibrator, order, tag):
            if ord == "b":
                calibrators_before.append((cal, "cal", tg))
            else:
                calibrators_after.append((cal, "cal", tg))
    else:
        if order == "b":
            calibrators_before.append((calibrator, "cal", tag))
        else:
            calibrators_after.append((calibrator, "cal", tag))
    return calibrators_before + [(target, "sci", None)] + calibrators_after


def create_ob(target: str,
              observational_type: str,
              array_configuration: str,
              operational_mode: Optional[str] = "st",
              sci_name: Optional[str] = None,
              tag: Optional[str] = None,
              resolution: Optional[str] = "low",
              connection: Optional[p2api] = None,
              container_id: Optional[int] = None,
              server: Optional[str] = "production",
              output_dir: Optional[Path] = None) -> None:
    """

    target : str
    observational_type : str
    array_configuration : str
        Determines the array configuration. Possible values are "UTs",
        "small", "medium", "large", "extended".
    operational_mode : str, optional
        The mode of operation for MATISSE. Can be either "st"/"standalone"
        for the MATISSE-standalone mode or "gr"/"gra4mat" for GRA4MAT.
        Default is standalone.
    sci_name : str, optional
    tag : str, optional
    resolution : str, optional
    connection : p2api, optional
    container_id : int, optional
    output_dir : path, optional
    """
    try:
        ob = compose_ob(target, observational_type,
                        array_configuration, operational_mode,
                        sci_name, tag, resolution)
        if container_id is not None:
            if connection is None:
                connection = login(server=server)
            upload_ob(connection, ob, container_id)

        if output_dir is not None:
            ob_name = set_ob_name(target, observational_type, sci_name, tag)
            write_ob(ob, ob_name, output_dir)
    except KeyError as e:
        print(f"[ERROR]: Failed creating OB '{target}'! See 'p2obp.log'.")
        logging.error("[ERROR]: Failed creating OB '{target}'!", exc_info=True)


def create_obs_from_lists(targets: List[str],
                          calibrators: Union[List[str], List[List[str]]],
                          orders: Union[List[str], List[List[str]]],
                          tags: Union[List[str], List[List[str]]],
                          operational_mode: str,
                          observational_type: str,
                          array_configuration: str,
                          resolution: Dict,
                          connection: p2api,
                          container_id: int,
                          output_dir: Path) -> None:
    """

    Parameters
    ----------
    targets : list of str
    calibrators : list of str or list of list of str
    orders : list of str or list of list of str
    tags : list of str or list of list of str
    operational_mode : str
        The mode MATISSE is operated in and for which the OBs are created.
        Either "st" for standalone, "gr" for GRA4MAT_ft_vis or "both",
        if obs for both are to be created. Default is "st".
    observational_mode : str, optional
        Can either be "vm" for Visitor Mode (VM) or "sm" for Service
        Mode (SM). Default is "vm".
    array_configuration : str
    resolution: dict, optional
        The default spectral resolutions for the obs in L-band. This is
        a dictionary containing as keys the individual science targets
        (the calibrators will be matched) and as values the resolution
        of the specific target. The values have to be either "low", "med"
        or "high". Default resolution is "low" and can be set via
        options["resolution"].
    connection : p2api
        The P2 python api.
    container_id : int
        The id that specifies the ob on p2.
    output_dir : path
        The output directory, where the (.obx)-files will be created in.
        If left at "None" no files will be created.
    """
    for mode in OPERATIONAL_MODES[operational_mode.lower()]:
        print(f"{'':-^50}")
        print(f"Creating OBs for {mode}-mode...")
        print(f"{'':-^50}")

        if not calibrators:
            calibrators = copy_list_and_replace_values(targets, "")
        if not tags:
            tags = copy_list_and_replace_values(calibrators, "LN")
        if not orders:
            orders = copy_list_and_replace_values(calibrators, "a")

        if output_dir is not None:
            mode_out_dir = output_dir / mode
            if not mode_out_dir.exists():
                mode_out_dir.mkdir(parents=True, exist_ok=True)
        else:
            mode_out_dir = output_dir

        if observational_type == "vm" and container_id is not None:
            mode_id = create_remote_container(connection, mode,
                                              container_id, observational_type)
        else:
            mode_id = None

        for target, calibrator, order, tag \
                in zip(targets, calibrators, orders, tags):
            if mode_out_dir is not None:
                target_dir = mode_out_dir / target
                if not target_dir.exists():
                    target_dir.mkdir(parents=True, exist_ok=True)
            else:
                target_dir = mode_out_dir

            if observational_type == "vm":
                if mode_id is not None:
                    target_id = create_remote_container(connection, target,
                                                        mode_id, observational_type)
                elif container_id is not None:
                    target_id = create_remote_container(connection, target,
                                                        container_id, observational_type)
                else:
                    target_id = None

            if resolution is not None and target in resolution:
                res = resolution[target]
            else:
                res = options["resolution"]

            unwrapped_lists = unwrap_lists(target, calibrator, order, tag)
            for (name, sci_cal_flag, tag) in unwrapped_lists:
                sci_name = target if sci_cal_flag == "cal" else None
                if not name:
                    continue
                create_ob(name, sci_cal_flag, array_configuration,
                          operational_mode, sci_name, tag, res,
                          connection, target_id, output_dir=target_dir)


# TODO: Write down how the runs need to be written down in the observing plan -> Make
# it automatic at some point
# TODO: Make print better if both uploading and making is active
# TODO: Log if nan appears in dataset or empty value
def create_obs_from_dict(night_plan: Dict,
                         operational_mode: str,
                         observational_mode: str,
                         resolution: Dict,
                         container_id: str,
                         username: str,
                         password: str,
                         server: str,
                         output_dir: Optional[Path] = None) -> None:
    """

    Also automatically gets the operational mode, the array_config,
    the resolution and the run's program id from the run name and if
    it cannot be detected, it will then prompts the user to input it
    manually.

    Parameters
    ----------
    night_plan : dict
        A dictionary containing a parsed night plan. If given
        it will automatically upload the obs to p2.
    operational_mode : str
        The mode MATISSE is operated in and for which the OBs are created.
        Either "st" for standalone, "gr" for GRA4MAT_ft_vis or "both",
        if obs for both are to be created. Default is "st".
    observational_mode : str, optional
        Can either be "vm" for Visitor Mode (VM) or "sm" for Service
        Mode (SM). Default is "vm".
    resolution: dict, optional
        The default spectral resolutions for the obs in L-band. This is
        a dictionary containing as keys the individual science targets
        (the calibrators will be matched) and as values the resolution
        of the specific target. The values have to be either "low", "med"
        or "high". Default resolution is "low" and can be set via
        options["resolution"].
    container_id : int
    username : str
        The p2 user name.
    password : str
        The p2 user password.
    server: str, optional
    output_dir : path
        The output directory, where the (.obx)-files will be created in.
        If left at "None" no files will be created.
    """
    connection = login(username, password, server)
    for run_key, run in night_plan.items():
        # TODO: Enable direct user input for these? Add more parameters?
        # Maybe make this parsing more robust?
        # TODO: Avoid program stoppage caused by this parsing errors and
        # just give user that information.
        if container_id is None:
            run_prog_id = parse_run_prog_id(run_key)
            run_id = get_remote_run(connection, run_prog_id)
        else:
            run_id = container_id
        array_config = parse_array_config(run_key)
        operational_mode = parse_operational_mode(run_key)
        # TODO: Make this so it automatically sets the option
        options["resolution"] = parse_run_resolution(run_key)

        # TODO: Improve this error and make it possible to also only
        # generated (.obx)-files.
        if output_dir is None and run_id is None:
            raise ValueError("Determining run id automatically"
                             " or via input has failed!")

        if output_dir is not None:
            run_name = ''.join(run_key.split(",")[0].strip().split())
            run_dir = output_dir / run_name
            if not run_dir.exists():
                run_dir.mkdir(parents=True, exist_ok=True)
        else:
            run_dir = None

        print(f"{'':-^50}")
        print(f"Creating OBs for {run_key}...")
        for night_key, night in run.items():
            print(f"{'':-^50}")

            night_name = parse_night_name(night_key)
            if observational_mode == "vm":
                night_id = create_remote_container(connection,
                                                   night_name,
                                                   run_id,
                                                   observational_mode)
            else:
                night_id = run_id

            if run_dir is not None:
                night_dir = run_dir / night_name
                print(f"Creating folder: '{night_dir.name}', and filling it with OBs...")
                if not night_dir.exists():
                    night_dir.mkdir(parents=True, exist_ok=True)
            else:
                night_dir = None

            create_obs_from_lists(*read_dict_to_lists(night), operational_mode,
                                  observational_mode, array_config, resolution,
                                  connection, night_id, night_dir)


# TODO: Think of implementation of uploading after parsing?
# TODO: Think of adding the `create_ob` script that combines `compose_ob` and 
# `upload_ob`.
def create_obs(night_plan: Optional[Path] = None,
               manual_input: Optional[List[List]] = None,
               operational_mode: str = "st",
               observational_mode: Optional[str] = "vm",
               resolution: Optional[Dict] = None,
               container_id: Optional[int] = None,
               username: Optional[str] = None,
               password: Optional[str] = None,
               server: Optional[str] = "production",
               output_dir: Optional[Path] = None) -> None:
    """

    Parameters
    ----------
    night_plan : path, optional
        A dictionary containing a parsed night plan. If given
        it will automatically upload the obs to p2.
    manual_input : list of lists, optional
        The manual input of the four needed lists
        [targets, calibrators, tags, order]. Only the "targets" and
        "calibrators" list need to be provided, "tags" and "order" can
        be autofilled.
    operational_mode : str, optional
        The mode MATISSE is operated in and for which the OBs are created.
        Either "st" for standalone, "gr" for GRA4MAT_ft_vis or "both",
        if obs for both are to be created. Default is "st".
    observational_mode : str, optional
        Can either be "vm" for Visitor Mode (VM) or "sm" for Service
        Mode (SM). Default is "vm".
    resolution: dict, optional
        The default spectral resolutions for the obs in L-band. This is
        a dictionary containing as keys the individual science targets
        (the calibrators will be matched) and as values the resolution
        of the specific target. The values have to be either "low", "med"
        or "high". Default resolution is "low" and can be set via
        options["resolution"].
    container_id : int, optional
        The id that specifies the ob on p2.
    username : str, optional
        The p2 user name.
    password : str, optional
        The p2 user password.
    server: str, optional
    output_dir: path, optional
        The output directory, where the (.obx)-files will be created in.
        If left at "None" no files will be created.
    """
    if night_plan is None and output_dir is None and container_id is None:
        raise IOError("Either output directory, container id or"
                      " night plan must be set!")

    if output_dir is not None:
        output_dir = Path(output_dir, "manualOBs")\
                if manual_input else Path(output_dir, "automaticOBs")
        # TODO: Apply here a removal of the old files

    if manual_input is not None:
        array_config = parse_array_config()
        try:
            targets, calibrators, orders, tags = manual_input
        except ValueError as exc:
            raise ValueError("In case of manual input four lists "
                             " (science_targets, calibrators, orders, tag)"
                             " must be given!") from exc
        if container_id is not None:
            connection = login(username, password, server)
        else:
            connection = None

        create_obs_from_lists(targets, calibrators, orders, tags,
                              operational_mode, observational_mode, array_config,
                              resolution, connection, container_id, output_dir)

    elif night_plan is not None:
        night_plan = parse_night_plan(night_plan)
        create_obs_from_dict(night_plan, operational_mode,
                             observational_mode, resolution, container_id,
                             username, password, server, output_dir)
    else:
        raise IOError("Neither manul input list or input"
                      " night plan path has been detected!")


if __name__ == "__main__":
    outdir = Path("/Users/scheuck/Data/observations/obs/")
    night_plan = Path("/Users/scheuck/Data/observations/CIAO/MATISSE_CIAO_UTs_plan_v2.txt")

    sci_lst = ["YLW 16A"]
    cal_lst = []
    order_lst, tag_lst = [], []
    manual_lst = [sci_lst, cal_lst, order_lst, tag_lst]

    res_dict = {}

    options["catalogs.local.active"] = "ciao"
    create_obs(night_plan=night_plan, container_id=3634531, username="MATISSETeam")
