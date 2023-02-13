"""The completely automated OB creation from parsing to upload"""
from pathlib import Path
from typing import Dict, List, Optional

from libs.parser import parse_night_plan
from libs.creator import ob_creation
from libs.uploader import ob_uploader
from libs.utils import get_password_and_username


def ob_pipeline(output_dir: Optional[Path] = "",
                manual_lst: Optional[List] = [],
                night_plan_path: Optional[Path] = "",
                resolution_dict: Optional[Dict] = {},
                save_yaml_file: Optional[bool] = True,
                upload: Optional[bool] = False) -> None:
    """

    Parameters
    ----------
    output_dir: Path, optional
    upload: bool, optional
    night_plan_path: Path, optional
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
        # TODO: Think of way how to implement this run_dict
        if save_yaml_file:
            run_dict = parse_night_plan(night_plan_path, save_path=output_dir)
        else:
            run_dict = parse_night_plan(night_plan_path)
        print("Parsing complete!")
        print("-------------------------------------------------------------------")

    print("Creating the OBs!")
    print("-------------------------------------------------------------------")
    ob_creation(output_dir, run_data=run_dict,
                res_dict=resolution_dict, manual_lst=manual_lst,
                mode="gr", upload_prep=upload)
    print("OB creation compete!")
    print("-------------------------------------------------------------------")

    if upload:
        print("Uploading the OBs!")
        print("-------------------------------------------------------------------")
        ob_uploader(output_dir, run_data=run_data, username=username, password=password)


if __name__ == "__main__":
    data_path = Path("/Users/scheuck/Data/observations/")
    out_path = Path("/Users/scheuck/Data/observations/obs")
    path = data_path / "P109/june2022" / "p109_observing_plan_v0.9_run3.txt"

    # The period and the proposal tag of the run
    run_data = ["109", "2313"]

    # NOTE: The resolution dict
    res_dict = {}

    ob_pipeline(output_dir=out_path, night_plan_path=path,
                save_yaml_file=True, upload=False)
