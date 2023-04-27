from pathlib import Path
from typing import Union, Optional, Any, Dict, List, Tuple

import numpy as np

from .backend.create import create_ob
from .backend.parse import parse_array_config, parse_run_resolution,\
    parse_run_prog_id, parse_night_name
from .backend.upload import upload_ob


OPERATIONAL_MODES = {"both": ["standalone", "GRA4MAT"],
                     "st": ["standalone"], "gr": ["GRA4MAT"]}


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


def create_obs_from_lists(targets: List[str],
                          calibrators: Union[List[str], List[List[str]]],
                          orders: Union[List[str], List[List[str]]],
                          tags: Union[List[str], List[List[str]]],
                          operational_mode: str,
                          observational_mode: str,
                          array_configuration: str,
                          resolution: Union[str, Dict],
                          container_id: int,
                          output_dir: Path) -> None:
    """

    Parameters
    ----------
    operational_mode : str
        The mode MATISSE is operated in and for which the OBs are created.
        Either "st" for standalone, "gr" for GRA4MAT_ft_vis or "both",
        if obs for both are to be created. Default is "st".
    observational_mode : str, optional
        Can either be "vm" for Visitor Mode (VM) or "sm" for Service
        Mode (SM). Default is "vm".
    array_configuration : str
    resolution : list, optional
        The default spectral resolutions for the obs in L-band. This can
        either be a string of ("low", "med", "high") or a dictionary containing
        as entries individual science targets (the calibrators will be
        matched).
        In case of a dictionary one can set a key called "standard" to set
        a standard resolution for all not listed science targets, if not this
        will default to "low".
    container_id : int
    output_dir : path
        The output directory, where the (.obx)-files will be created in.
        If left at "None" no files will be created.
    """
    for mode in OPERATIONAL_MODES[operational_mode]:
        print(f"{'':^-50}")
        print(f"Creating OBs for {mode}-mode...")
        print(f"{'':^-50}")

        if not tags:
            tags = copy_list_and_replace_values(calibrators, "LN")
        if not orders:
            orders = copy_list_and_replace_values(calibrators, "a")

        # TODO: Implement here p2 folder creation and check for OB-creation
        if output_dir is not None:
            mode_out_dir = output_dir / mode
            if not mode_out_dir.exists():
                mode_out_dir.mkdir(parents=True, exist_ok=True)

        # TODO: Make creation for folders different for service and visitor mode
        if observational_mode == "vm":
            ...

        # TODO: Add proper for loops
        # TODO: Think how to order the OB-creation here
        for target, calibrator in zip(targets, calibrators):
            if isinstance(resolution, dict):
                if target in resolution:
                    resolution = resolution[target]
                elif "standard" in resolution:
                    resolution = resolution["standard"]
                else:
                    resolution = "low"

            create_ob(target, "sci", array_configuration, operational_mode,
                      resolution=resolution, output_dir=output_dir)
            if isinstance(calibrator, list):
                for cal, ord, sub_tag in zip(calibrator, order, tag):
                    create_ob(cal, "cal", array_configuration, operational_mode,
                              sci_name=target, tag=sub_tag,
                              resolution=resolution, output_dir=output_dir)
            else:
                create_ob(calibrator, "cal", array_configuration,
                          operational_mode, sci_name=target, tag=tag,
                          resolution=resolution, output_dir=output_dir)


# TODO: Write down how the runs need to be written down in the observing plan -> Make
# it automatic at some point
def create_obs_from_dict(night_plan: Dict,
                         operational_mode: str,
                         observational_mode: str,
                         resolution: str,
                         output_dir: Optional[Path] = None) -> None:
    """

    Also automatically gets the array_config from the run name and if not
    possible then prompts the user to input it

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
    resolution : list, optional
        The default spectral resolutions for the obs in L-band. This can
        either be a string of ("low", "med", "high") or a dictionary containing
        as entries individual science targets (the calibrators will be
        matched).
        In case of a dictionary one can set a key called "standard" to set
        a standard resolution for all not listed science targets, if not this
        will default to "low".
    output_dir : path
        The output directory, where the (.obx)-files will be created in.
        If left at "None" no files will be created.
    """
    for run_key, run in night_plan.items():
        print(f"{'':^-50}")
        print(f"Creating OBs for {run_key}...")

        if observational_mode == "sm":
            resolution = parse_run_resolution(run_key)
            operational_mode = get_run_operational_mode(run_key)

        run_name = ''.join(run_key.split(",")[0].strip().split())
        if output_dir is not None:
            run_dir = output_dir / run_name
            if not run_dir.exists():
                run_dir.mkdir(parents=True, exist_ok=True)
        else:
            run_dir = None

        array_config = parse_array_config(run_key)
        for night_id, night in run.items():
            # TODO: Implement here p2 folder creation and check for OB-creation
            print(f"{'':^-50}")
            night_name = parse_night_name(night_id)
            if run_dir is not None:
                night_dir = run_dir / night_name
                print(f"Creating folder: '{night_dir.name}', and filling it with OBs...")
            else:
                night_dir = None

            if not night_dir.exists():
                night_dir.mkdir(parents=True, exist_ok=True)

            create_obs_from_lists(*read_dict_to_lists(night), operational_mode,
                                  observational_mode, array_config,
                                  resolution, container_id, night_dir)


def create_obs(night_plan: Optional[Dict] = None,
               manual_input: Optional[List[List]] = None,
               operational_mode: str = "st",
               observational_mode: Optional[str] = "vm",
               resolution: Optional[Union[str, Dict]] = "low",
               container_id: Optional[int] = None,
               output_dir: Optional[Path] = None) -> None:
    """

    Parameters
    ----------
    night_plan : dict, optional
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
    resolution: str or dict, optional
        The default spectral resolutions for the obs in L-band. This can
        either be a string of ("low", "med", "high") or a dictionary containing
        as entries individual science targets (the calibrators will be
        matched).
        In case of a dictionary one can set a key called "standard" to set
        a standard resolution for all not listed science targets, if not this
        will default to "low".
    container_id : int
    output_dir: path, optional
        The output directory, where the (.obx)-files will be created in.
        If left at "None" no files will be created.
    """
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
        create_obs_from_lists(targets, calibrators,
                              orders, tags, operational_mode,
                              observational_mode, array_config,
                              resolution, container_id, output_dir)

    elif night_plan is not None:
        create_obs_from_dict(night_plan, operational_mode,
                             observational_mode, resolution, output_dir)
    else:
        raise IOError("Neither '.yaml'-file nor input list found or input"
                      " dict found!")


if __name__ == "__main__":
    outdir = Path("/Users/scheuck/Data/observations/obs/")

    sci_lst = ["Beta Leo", "HD 100453"]
    cal_lst = ["HD100920", "HD102964"]
    order_lst, tag_lst = [], []
    manual_lst = [sci_lst, cal_lst, order_lst, tag_lst]

    res_dict = {}

    create_obs(outdir, manual_input=manual_lst,
               operational_mode="both", resolution="low")

    # TOOD: Add night astronomer comments to template of Jozsefs -> Rewrite his script?
    # TODO: Find way to switch of photometry of template -> Jozsef's script rewrite?


    # def 
    #
    #     if run_prog_id is None:
    #         run_prog_id = get_run_prog_id(upload_directory, obx_folder)
    #         run_id = get_remote_run(p2_connection, run_prog_id)
    #     container_ids, containers =\
    #             create_folder_structure_and_upload(p2_connection, upload_directory,
    #                                                obx_folder, run_id,
    #                                                container_ids, containers,
    #                                                observation_mode)

