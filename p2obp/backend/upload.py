import sys
import getpass
from pprint import pprint
from typing import Optional, Dict, List, Tuple

import json
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
                    "SEQ.OFFSET.ALPHA": float,
                    "SEQ.OFFSET.DELTA": float,
                    "SEQ.PHOTO.ST": bool,
                    "SEQ.SKY.OFFS.ALPHA": float,
                    "SEQ.SKY.OFFS.DELTA": float,
                    "SEQ.TRACK.BAND": str,
                    "INS.DIL.NAME": str,
                    "INS.DIN.NAME": str,
                    "DPR.CATG": str}


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


def create_ob(connection: p2api, container_id: int, header: Dict) -> int:
    """

    Parameters
    ----------

    Returns
    -------
    """
    print(f"Creating OB '{header['user']['name']}'...")
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
    print(f"\tAdding template '{content[template_name]}'...")
    template, version = connection.createTemplate(ob_id, content[template_name])
    template, version = connection.setTemplateParams(ob_id, template, content, version)



def upload_ob(ob: Dict, container_id: int,
              username: Optional[str] = None,
              password: Optional[str] = None,
              server: Optional[str] = "production"):
    """"""
    connection = login(username, password, server)
    ob_id = create_ob(connection, container_id, ob["header"])
    acq_template = add_template(connection, ob_id, ob, "acquisition")
    obs_template = add_template(connection, ob_id, ob, "observation")
