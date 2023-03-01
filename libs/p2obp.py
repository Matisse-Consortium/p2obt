"""The completely automated OB creation from parsing to upload"""
from pathlib import Path
from typing import Dict, List, Optional

from parser import parse_night_plan
from creator import ob_creation
from uploader import ob_uploader
from utils import get_password_and_username


# TODO: Change Jozef's script so that the Guide Stars are automatically put in (with a
# comment of the Guide star's name)
def ob_pipeline(output_dir: Optional[Path] = None,
                manual_lst: Optional[List] = None,
                night_plan_path: Optional[Path] = None,
                mode_selection: Optional[str] = "gr",
                observation_mode: Optional[str] = "visitor",
                resolution_dict: Optional[Dict] = {},
                save_to_yaml: Optional[bool] = False,
                upload: Optional[bool] = False) -> None:
    """

    Parameters
    ----------
    output_dir: Path, optional
    upload: bool, optional
    night_plan_path: Path, optional
    mode_selection: str, optional
    observation_mode: str, optional
        Can either be "visitor" for Visitor Mode (VM) or "service" for Service Mode (SM)
    resolution_dict: Dict, optional
    save_yaml_file: bool, optional
    upload: bool, optional
    """
    output_dir = output_dir if output_dir else Path().cwd()
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    # TODO: At some point exchange this with proper password getter
    if upload:
        username, password = get_password_and_username()

    if night_plan_path:
        print("Parsing the Night plan!")
        print("-------------------------------------------------------------------")
        if save_to_yaml:
            night_plan_data = parse_night_plan(night_plan_path, save_path=output_dir)
        else:
            night_plan_data = parse_night_plan(night_plan_path)
        print("Parsing complete!")
        print("-------------------------------------------------------------------")

    print("Creating the OBs!")
    print("-------------------------------------------------------------------")
    ob_creation(output_dir, night_plan_data=night_plan_data,
                res_dict=resolution_dict, manual_lst=manual_lst,
                mode_selection=mode_selection, observation_mode=observation_mode,
                clean_previous=True)
    print("-------------------------------------------------------------------")
    print("OB creation compete!")
    print("-------------------------------------------------------------------")

    if upload:
        print("Uploading the OBs!")
        print("-------------------------------------------------------------------")
        ob_uploader(output_dir / "automaticOBs", username=username,
                    password=password, observation_mode=observation_mode)


if __name__ == "__main__":
    data_dir = Path("/Users/scheuck/Data/observations/")
    output_dir = Path("/Users/scheuck/Data/observations/obs")
    period_dir = data_dir / "P111"
    night_plan_path = period_dir / "runs_v1" / "run009_v1.txt"

    # TODO: Make also a DIT-dictionary where ppl can change the dit of an individual thing
    # or make it possible to change either both or once at a time?
    # TODO: Add Service Mode, where all contents of the run are posted to it by upload
    # NOTE: The resolution dict
    res_dict = {}

    ob_pipeline(output_dir=output_dir, night_plan_path=night_plan_path,
                save_to_yaml=False, upload=True, observation_mode="service")
