import logging
from pathlib import Path
from typing import Dict, List
from warnings import warn

from p2api.p2api import ApiConnection

from .backend.compose import compose_ob, set_ob_name, write_ob
from .backend.parse import (
    parse_array_config,
    parse_night_name,
    parse_night_plan_to_dict,
    parse_observation_type,
    parse_operational_mode,
    parse_resolution,
    parse_run_prog_id,
)
from .backend.upload import create_remote_container, get_remote_run, login, upload_ob
from .backend.utils import create_night_plan_dict

# FIXME: The RA and DEC (and probs pmra and pmdec) are wrong -> Simbad err, fix!
# Check the conversion of the queried values.
# TODO: The local file resolution overwrite might not work anymore.
# Is it needed?
# TODO: Make this shorter? Or into an option even?
OPERATIONAL_MODES = {
    "st": ["standalone"],
    "gr": ["GRA4MAT"],
    "matisse": ["standalone"],
    "gra4mat": ["GRA4MAT"],
}


def create_ob(
    target: str,
    ob_kind: str,
    array: str,
    mode: str = "st",
    sci_name: str | None = None,
    tag: str | None = None,
    resolution: str = "low",
    connection: ApiConnection | None = None,
    container_id: int | None = None,
    store_password: bool = True,
    remove_password: bool = False,
    user_name: str | None = None,
    server: str = "production",
    output_dir: Path | None = None,
) -> None:
    """Creates a singular OB either locally or on P2.

    Parameters
    ----------
    target : str
        The name of the target.
    ob_kind : str
        The type of OB. If it is a science target ("sci") or a calibrator ("cal").
    array_configuration : str
        Determines the array configuration. Possible values are "UTs",
        "small", "medium", "large", "extended".
    operational_mode : str, optional
        The mode of operation for MATISSE. Can be either "st"/"standalone"
        for the MATISSE-standalone mode or "gr"/"gra4mat" for GRA4MAT.
        Default is standalone.
    sci_name : str, optional
        The name of the science target. If the OB is a science OB, this
        is None.
    tag : str, optional
        The calibrator tag (L, N or LN).
    resolution : str, optional
        The resolution of the OB. Can be either "low", "med" or "high".
    connection : ApiConnection, optional
        The connection to the P2 database.
    container_id : int, optional
        The id of the container on P2.
    user_name : str, optional
        The user name for the P2 database.
    server : str, optional
        The server to connect to. Can be either "production" or "test".
    output_dir : path, optional
        The output directory, where the (.obx)-files will be created in.
        If left at "None" no files will be created.
    """
    try:
        if container_id is not None:
            if connection is None:
                connection = login(user_name, store_password, remove_password, server)
        if sci_name is not None and ob_kind == "sci":
            warn(
                "[WARNING]: The OB was specified as a science OB,"
                " but a science target name was separately specified."
                " It will be changed to a calibrator."
            )
            ob_kind = "cal"
        ob = compose_ob(
            target,
            ob_kind,
            array,
            mode,
            sci_name,
            tag,
            resolution,
        )
        upload_ob(connection, ob, container_id)

        if output_dir is not None:
            write_ob(ob, set_ob_name(target, ob_kind, sci_name, tag), output_dir)

    except KeyError:
        print(f"Failed creating OB '{target}'! See 'p2obt.log'.")
        logging.error(f"Failed creating OB '{target}'!", exc_info=True)


def create_obs(
    night_plan: Path | None = None,
    container_id: int | None = None,
    targets: List[str] | None = None,
    calibrators: List[List[str] | str] | None = None,
    orders: List[List[str] | str] | None = None,
    tags: List[List[str] | str] | None = None,
    resolution: Dict[str, str] | List[str] | str | None = "low",
    configuration: Dict[str, str] | List[str] | str | None = None,
    modes: Dict[str, str] | List[str] | str | None = "gr",
    user_name: str | None = None,
    store_password: bool | None = True,
    remove_password: bool | None = False,
    server: str | None = "production",
    output_dir: Path | None = None,
) -> None:
    """Creates the OBs from a night-plan parsed dictionary or from
    a manual input of the four needed lists.

    Parameters
    ----------
    night_plan : path, optional
        A dictionary containing a parsed night plan. If given
        it will automatically upload the obs to p2.
    container_id : int, optional
        The id that specifies the container on p2.
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
    user_name : str, optional
        The p2 user name.
    server: str, optional
        The server to connect to. Can be either "production" or "test".
    output_dir: path, optional
        The output directory, where the (.obx)-files will be created in.
        If left at "None" no files will be created.
    """
    if night_plan is None and output_dir is None and container_id is None:
        raise IOError(
            "Either output directory, container id or night plan must be provided!"
        )

    if output_dir is not None:
        output_dir = (
            Path(output_dir, "manualOBs")
            if targets
            else Path(output_dir, "automaticOBs")
        )
        # TODO: Apply here a removal of the old files

    if night_plan is None:
        night_plan = create_night_plan_dict(
            targets, calibrators, orders, tags, resolution, configuration, modes
        )
    else:
        night_plan = parse_night_plan_to_dict(night_plan)

    if night_plan is None:
        raise IOError(
            "Targets, calbirators and their orders must either input manually"
            "or a path to a night plan provided!"
        )

    if output_dir is None:
        connection = login(user_name, store_password, remove_password, server)
    else:
        connection, run_id = None, None

    for run_key, nights in night_plan.items():
        array = parse_array_config(run_key)
        mode = parse_operational_mode(run_key)
        res = parse_resolution(run_key)
        ob_type = parse_observation_type(run_key)
        for night in list(nights.values())[0]:
            night.update(
                {
                    "array": array or night["array"],
                    "mode": mode or night["mode"],
                    "res": res or night["res"],
                    "type": ob_type or night["type"],
                }
            )

        if connection is not None:
            run_dir = None
            if container_id is None:
                run_prog_id = parse_run_prog_id(run_key)
                run_id = get_remote_run(connection, run_prog_id)
            else:
                run_id = container_id
        else:
            run_dir = output_dir / "".join(run_key.split(",")[0].strip().split())
            run_dir.mkdir(parents=True, exist_ok=True)

        print(f"{'':-^50}")
        print(f"Creating OBs for {run_key}...")
        for night_key, night in nights.items():
            print(f"{'':-^50}")
            night_name = parse_night_name(night_key)
            if night_name != "full_night":
                print(f"Creating OBs for {night_name}")
                print(f"{'':-^50}")

            if ob_type == "vm" and run_id is not None:
                night_id = create_remote_container(
                    connection, night_name, run_id, "folder"
                )
            else:
                night_id = run_id

            if run_dir is not None:
                night_dir = run_dir / night_name
                print(f"Creating folder '{night_dir.name}...'")
                night_dir.mkdir(parents=True, exist_ok=True)
            else:
                night_dir = None

            ids = {}
            for block in night:
                target = block["target"].replace(" ", "_")
                if night_dir is not None:
                    target_dir = night_dir / target
                    target_dir.mkdir(parents=True, exist_ok=True)
                else:
                    target_dir = None

                if night_id is not None:
                    if block["type"] in ["ts", "im"]:
                        container_type = (
                            "group" if block["type"] == "im" else "timelink"
                        )
                        if target not in ids:
                            ids[target] = create_remote_container(
                                connection, f"Image-{target}", night_id, container_type
                            )

                    image_entry = ids.get(target, None)

                    # TODO: Make sure that the convention is correct (imaging runs)
                    # TODO: Make different names for OB and SCI target
                    # TODO: Do the same for the OB name if im run (or time series?)
                    if image_entry is not None:
                        container_name = f"{target}-{block['array']}"
                    else:
                        container_name = target
                    # TODO: Also add time link for time series here

                    # TODO: Does this need to be a folder here for visitor mode or not?
                    # TODO: Fix this so that OBs are always created in the right group
                    target_id = create_remote_container(
                        connection,
                        container_name,
                        image_entry if image_entry is not None else night_id,
                        "concatenation",
                    )
                else:
                    target_id = None

                before_ind = [
                    i for i, cal in enumerate(block["cals"]) if cal.get("order") == "b"
                ]
                after_ind = [
                    i for i, cal in enumerate(block["cals"]) if cal.get("order") == "a"
                ]

                for ind in [*before_ind, "target", *after_ind]:
                    if ind != "target":
                        cal, sci_name = block["cals"][ind], block["target"]
                        target, tag, ob_kind = cal["name"], cal["tag"], "cal"
                    else:
                        target, sci_name, ob_kind, tag = (
                            block["target"],
                            None,
                            "sci",
                            None,
                        )

                    create_ob(
                        target,
                        ob_kind,
                        block["array"],
                        block["mode"],
                        sci_name,
                        tag,
                        block["res"],
                        connection,
                        target_id,
                        output_dir=target_dir,
                    )

    # TODO: Add some color here :D
    print("Done!")
