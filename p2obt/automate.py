import logging
from pathlib import Path
from typing import Dict, List
from warnings import warn

from p2api.p2api import ApiConnection

from .backend.compose import compose_ob, set_ob_name, write_ob
from .backend.parse import (
    parse_array_config,
    parse_night_name,
    parse_night_plan,
    parse_operational_mode,
    parse_run_prog_id,
    parse_run_resolution,
)
from .backend.upload import create_remote_container, get_remote_run, login, upload_ob


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
    operational_mode: str = "st",
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
            operational_mode,
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


# TODO: Finish this
def create_obs(
    night_plan: Path | None = None,
    manual_input: List[List] | None = None,
    observation_type: str | None = "sm",
    container_id: int | None = None,
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
    manual_input : list of lists, optional
        The manual input of the four needed lists
        [targets, calibrators, tags, order]. Only the "targets" and
        "calibrators" list need to be provided, "tags" and "order" can
        be autofilled.
    mode : str, optional
        The mode MATISSE is operated in and for which the OBs are created.
        Either "st" for standalone, "gr" for GRA4MAT_ft_vis or "both",
        if obs for both are to be created. Default is "st".
    observational_mode : str
        Can either be "vm" for visitor mode (VM), "sm" for service mode (SM),
        time series (TS), or imageing (IM).
    resolution: dict, optional
        The default spectral resolutions for the obs in L-band. This is
        a dictionary containing as keys the individual science targets
        (the calibrators will be matched) and as values the resolution
        of the specific target. The values have to be either "low", "med"
        or "high". Default resolution is "low" and can be set via
        options["resolution"].
    container_id : int, optional
        The id that specifies the ob on p2.
    user_name : str, optional
        The p2 user name.
    server: str, optional
    output_dir: path, optional
        The output directory, where the (.obx)-files will be created in.
        If left at "None" no files will be created.
    """
    if night_plan is None and output_dir is None and container_id is None:
        raise IOError(
            "Either output directory, container id or" " night plan must be set!"
        )

    if output_dir is not None:
        output_dir = (
            Path(output_dir, "manualOBs")
            if manual_input
            else Path(output_dir, "automaticOBs")
        )
        # TODO: Apply here a removal of the old files

    if night_plan is None:
        # TODO: Make a night plan here from the manual input and then only use the dicts
        # for the OB creation.
        array = parse_array_config()

        if container_id is not None:
            connection = login(user_name, store_password, remove_password, server)
        else:
            connection = None

        ...
    else:
        night_plan = parse_night_plan(night_plan)

    if night_plan is None:
        raise IOError(
            "Targets, calbirators and their orders must either input manually"
            "or a path to a night plan provided!"
        )

    if output_dir is None:
        connection = login(user_name, store_password, remove_password, server)
    else:
        connection, run_id = None, None

    # TODO: Add in documentation that global setting overwrites local setting
    # also add that now comments are counted as settings for individual blocks
    for run_key, nights in night_plan.items():
        array = parse_array_config(run_key)
        mode = parse_operational_mode(run_key)
        resolution = parse_run_resolution(run_key)
        for night in list(nights.values())[0]:
            night.update(
                {
                    "array": array or night["array"],
                    "mode": mode or night["mode"],
                    "res": resolution or night["res"],
                }
            )

        if output_dir is None:
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

            # TODO: Add here? the imaging and time series mode
            if observation_type == "vm" and connection is not None:
                night_id = create_remote_container(
                    connection, night_name, run_id, observation_type
                )
            else:
                night_id = run_id
            # TODO: Finish the night id here

            if run_dir is not None:
                night_dir = run_dir / night_name
                print(f"Creating folder '{night_dir.name}...'")
                night_dir.mkdir(parents=True, exist_ok=True)
            else:
                night_dir = None

            for block in night:
                target = block["target"].replace(" ", "_")
                if output_dir is not None:
                    target_dir = output_dir / target
                    target_dir.mkdir(parents=True, exist_ok=True)
                else:
                    target_dir = None

                if container_id is not None:
                    target_id = create_remote_container(
                        connection, target, container_id, observation_type
                    )
                elif night_id is not None:
                    target_id = create_remote_container(
                        connection, target, night_id, observation_type
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
                        target, sci_name, ob_kind, tag = block["target"], None, "sci", None

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
    print("[INFO]: Done!")
