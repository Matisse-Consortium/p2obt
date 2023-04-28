import sys
import getpass
from typing import Optional, Dict

import numpy as np
import p2api


# TODO: Credit the guy for loadobx.py
TARGET_MAPPING = {"TARGET.NAME": "name",
                  "ra": "ra",
                  "dec": "dec",
                  "propRA": "properMotionRa",
                  "propDec": "properMotionDec",
                  "diffRA": "differentialRa",
                  "diffDec": "differentialDec",
                  "equinox": "equinox",
                  "epoch": "epoch"}

CONSTRAINTS_MAPPING = {"CONSTRAINT.SET.NAME": "name",
                       "sky_transparency": "skyTransparency",
                       "air_mass": "airmass",
                       "fractional_lunar_illumination": "fli",
                       "moon_angular_distance": "moonDistance",
                       "watervapour": "waterVapour",
                       "atm": "atm"}

TEMPLATE_MAPPING = {"ACQUISITION.TEMPLATE.NAME": str,
                    "SEQ.TARG.FLUX.L": float,
                    "SEQ.TARG.FLUX.N": float,
                    "SEQ.TARG.MAG.H": float,
                    "SEQ.TARG.MAG.K": float,
                    "TEL.TARG.ADDVELALPHA": float,
                    "TEL.TARG.ADDVELDELTA": float,
                    "COU.AG.ALPHA": str,
                    "COU.AG.DELTA": str,
                    "COU.AG.EPOCH": float,
                    "COU.AG.EQUINOX": float,
                    "COU.AG.GSSOURCE": str,
                    "COU.AG.PMA": float,
                    "COU.AG.PMD": float,
                    "COU.AG.TYPE": str,
                    "COU.GS.MAG": float,
                    "ISS.BASELINE": list,
                    "ISS.VLTITYPE": list,
                    "TEMPLATE.NAME": str,
                    "DET1.DIT": float,
                    "DET1.READ.CURNAME": str,
                    "SEQ.DIL.USER.WL0": float,
                    "SEQ.DIL.WL0": float,
                    "SEQ.FRINGES.NCYCLES": float,
                    "SEQ.OFFSET.ALPHA": list,
                    "SEQ.OFFSET.DELTA": list,
                    "SEQ.PHOTO.ST": bool,
                    "SEQ.SKY.OFFS.ALPHA": float,
                    "SEQ.SKY.OFFS.DELTA": float,
                    "SEQ.TRACK.BAND": str,
                    "INS.DIL.NAME": str,
                    "INS.DIN.NAME": str,
                    "DPR.CATG": str}

# TODO: Hard code this and check for upload
README_TEMPLATE = {"Date": "", "Main observer": "",
                   "e-mail": "", "Phone number": "",
                   "Skype": "", "Zoom": ""}


def login(username: Optional[str] = None,
          password: Optional[str] = None,
          server: Optional[str] = "demo"):
    """Login to the p2 API with the given username. Return the API connection.
    Parameters
    ----------
    username : str, optional
        The p2 user name.
    password : str, optional
        If none is given, then it will ask for it.
    server: str, optional
        Either "demo", "production" for paranal or "production_lasilla" for la
        silla.
    """
    password_prompt = "Input your ESO-password: "
    if username is None:
        username = input("Input your ESO-username: ")

    if password is None:
        if sys.platform == 'ios':
            import console
            password = console.password_alert(password_prompt)
        elif sys.stdin.isatty():
            password = getpass.getpass(password_prompt)
        else:
            # TODO: Remove this, too unsafe?
            password = input(password_prompt)
    return p2api.ApiConnection(server, username, password)


def get_remote_run(connection: p2api, run_id: str) -> Optional[int]:
    """Gets the run that corresponds to the period, proposal and the number and
    returns its runId.

    Parameters
    ----------
    connection : p2api
        The p2ui python api.
    run_id : str
        The run's id in the format <period.proposal_tag.run_number>.

    Returns
    -------
    run_id : int, optional
        The run's id that can be used to access and modify it with the p2api.
        If not found return "None".
    """
    for run in connection.getRuns()[0]:
        if run_id == run["progId"]:
            return run["containerId"]
    return None


def remote_container_exists(connection: p2api, container_id: int) -> bool:
    """Checks if the container with this id exists on p2.

    Parameters
    ----------
    connection : p2api
        The p2ui python api.
    container_id : int
        The id of the container on p2.

    Returns
    -------
    container_exists : bool
        'True' if container exists, otherwise 'False'.
    """
    try:
        if connection.getContainer(container_id):
            return True
    except p2api.p2api.P2Error:
        pass
    return False


def create_remote_container(connection: p2api,
                            name: str, container_id: int,
                            observational_mode: Optional[str] = "vm") -> int:
    """Creates a container on p2.

    Parameters
    ----------
    connection : p2api
        The P2 python api.
    name: str
        The container's name.
    container_id : int
        The id that specifies the container.
    observational_mode : str
        Can either be "vm" for visitor mode (VM) or "sm" for service mode (SM).

    Returns
    -------
    container_id : int
        The created container's id.
    """
    print(f"Creating container '{name}' on p2...")
    if observational_mode == "vm":
        container, _ = connection.createFolder(container_id, name)
    elif observational_mode == "sm":
        container, _ = connection.createConcatenation(container_id, name)
    else:
        raise IOError("No such operation mode exists!")
    return container["containerId"]


# TODO: Make logger here
def create_ob(connection: p2api, container_id: int, header: Dict) -> int:
    """

    Parameters
    ----------

    Returns
    -------
    """
    ob, version = connection.createOB(container_id, header["user"]["name"])
    ob["instrument"] = header["observation"]["instrument"]
    ob["obsDescription"]["name"] = header["user"]["name"]
    ob["obsDescription"]["userComments"] = header["user"]["userComments"]
    for key, value in header.items():
        if key not in ob:
            continue
        if key == "target":
            mapping = TARGET_MAPPING
        if key == "constraints":
            mapping = CONSTRAINTS_MAPPING
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                if sub_key not in mapping:
                    continue
                ob[key][mapping[sub_key]] = sub_value
    ob, version = connection.saveOB(ob, version)
    return ob["obId"]


def apply_mapping(content: Dict, mapping: Dict) -> None:
    """Applies mapping to make template serializable."""
    for key, value in content.items():
        if key in mapping:
            if isinstance(value, mapping[key]):
                continue
            if mapping[key] == list:
                value = [value]
            elif mapping[key] == float:
                if isinstance(value, (np.float32, np.float64)):
                    value = value.item()
                else:
                    value = float(value)
                value = round(value, 2)
            elif mapping[key] == str:
                value = str(value)
            elif mapping[key] == bool:
                value = True if value == "T" else False
        content[key] = value


def add_template(connection: p2api, ob_id: int, ob: Dict, template_kind: str) -> None:
    """Adds template to an (.obx)-file on the p2.

    Parameters
    ----------
    connection : p2api
    ob_id : int
    ob : dict
    template_kind : str
    """
    template_name = "TEMPLATE.NAME"
    if template_kind == "acquisition":
        template_name = f"ACQUISITION.{template_name}"
    content = ob[template_kind]
    apply_mapping(content, TEMPLATE_MAPPING)
    print(f"\t\tAdding template '{content[template_name]}'...")
    template, version = connection.createTemplate(ob_id, content[template_name])
    template, version = connection.setTemplateParams(ob_id, template, content, version)


def upload_ob(connection: p2api,
              ob: Dict, container_id: int) -> None:
    """

    Parameters
    ----------

    Returns
    -------
    """
    ob_name = ob['header']['user']['name']
    print(f"\tCreating OB '{ob_name}'...")
    try:
        ob_id = create_ob(connection, container_id, ob["header"])
        add_template(connection, ob_id, ob, "acquisition")
        add_template(connection, ob_id, ob, "observation")
    except p2api.P2Error:
        print(f"[ERROR]: Failed creating OB '{ob_name}'!")
