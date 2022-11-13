"""The completely automated OB creation from parsing to upload"""
import os

from pathlib import Path
from typing import Optional

from lib.parser import parse_night_plan
from lib.creator import ob_creation
from lib.uploader import ob_uploader
from lib.utils import get_password_and_username


def ob_pipeline(output_dir: Optional[Path] = "",
                manual_lst: Optional[List] = [],
                night_plan_path: Optional[Path] = "",
                resolution_dict: Optional[Dict] = {},
                upload: Optional[bool] = False) -> None:
    """

    Parameters
    ----------
    output_dir: Path, optional
    upload: bool, optional
    night_plan_path: Path, optional
    resolution_dict: Dict, optional
    """
    output_dir = output_dir if output_dir else os.getcwd()

    # TODO: At some point exchange this with proper password getter
    username, password = get_password_and_username()

    if night_plan_path:
        print("Parsing the Night plan!")
        print("-------------------------------------------------------------------")
        run_dict = parse_night_plan(night_plan_path, save2file=True)
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
    data_path = "/Users/scheuck/Documents/data/observations/"
    out_path = "/Users/scheuck/Documents/data/observations/phase2/obs"
    path = os.path.join(data_path, "P109/september2022", "p109_observing_plan_v0.1.txt")

    # The period and the proposal tag of the run
    run_data = ["109", "2313"]

    # NOTE: The resolution dict
    res_dict = {}

    ob_pipeline(night_plan_path=path, upload=False)
