"""Night Plan Parser

This script parses the night plans made with Roy van Boekel's "calibrator_find"
IDL script into a (.yaml)-file that contains the CALs sorted to their
corresponding SCI-targets in a dictionary  of the following structure

It first specifies the run, then the individual night with the corresponding the SCIs,
CALs and TAGs (The Tags show if the calibrator is N-, L-band or both)

The night plan has to be a (.txt)-file or of a similar filetype/file

This file can also be imported as a module and contains the following functions:
    * _get_file_section - Gets a section of the (.txt)/lines
    * _get_targets_calibrators_tags - Creates a lists containing nested lists with the
                                      SCI, CAL and TAG information
    * parse_night_plan - Parses the night plan -> The main function of this script

Example of usage:
    >>> from parser import parse_night_plan
    >>> run_dict = parse_night_plan(path_to_file, save_path="")
    >>> print(run_dict)
    ... {'run 5, 109.2313.005 = 0109.C-0413(E)': {'nights 2-4: {'SCI': ['MY Lup', ...],
    ...  'CAL': [['HD142198'], ...], 'TAG': [['LN'], ...]}}}
"""
# TODO: Make parser accept more than one calibrator block for one night, by
# checking if there are integers for numbers higher than last calibrator and
# then adding these

from re import split
import yaml

from pathlib import Path
from collections import namedtuple
from typing import Any, Dict, List, Optional

from utils import contains_element


def parse_line(parts: str) -> str:
    """Parses a line from the `calibrat_find`-tool and returns the objects name

    Parameters
    ----------
    parts: str

    Returns
    -------
    target_name: str
    """
    target_name_cutoff = len(parts)
    for index, part in enumerate(parts):
        if index <= len(parts)-4:
            if part.isdigit() and parts[index+1].isdigit()\
               and "." in parts[index+2] and not index == len(parts)-4:
                target_name_cutoff = index
                break
    return " ".join(parts[1:target_name_cutoff])


def parse_groups(section: List):
    """Parses any combination of a calibrator-science target block into a dictionary
    containing all the blocks information"""
    data = {}
    calibrator_labels = ["name", "order", "tag"]
    current_group, current_science_target = [], None

    for line in section:
        parts = line.strip().split()

        if not parts:
            # HACK: Remove the None values so to say, manually
            if current_science_target is not None:
                data[current_science_target] = current_group
            current_group, current_science_target = [], None
            continue
        if line.startswith("#") or not line[0].isdigit():
            continue

        obj_name = parse_line(parts)
        if obj_name.startswith("cal_"):
            tag = obj_name.split("_")[1]
            order = "b" if current_science_target is None else "a"
            calibrator = dict(zip(calibrator_labels,
                                  [obj_name.split("_")[2], order, tag]))
            current_group.append(calibrator)
        else:
            current_science_target = obj_name
    return data


def _get_file_section(lines: List, identifier: str) -> Dict:
    """Gets the section of a file corresponding to the given identifier and
    returns a dict with the keys being the match to the identifier and the
    values being a subset of the lines list

    Parameters
    ----------
    lines: List
        The lines read from a file
    identifier: str
        The identifier by which they should be split into subsets

    Returns
    --------
    subset: dict
        A dict that contains a subsets of the original lines
    """
    indices, labels = [], []
    for index, line in enumerate(lines):
        if line.lower().startswith(identifier):
            indices.append(index)
            labels.append(line.replace('\n', ''))

    if not indices:
        indices, labels = [0], ["full_" + identifier]

    sections = [lines[index:] if index == indices[~0] else \
                  lines[index:indices[i+1]] for i, index in enumerate(indices)]
    return {labels: sections for (labels, sections) in zip(labels, sections)}


def parse_night_plan(night_plan_path: Path,
                     run_identifier: Optional[str] = "run",
                     night_identifier: Optional[str] = "night",
                     save_path: Optional[Path] = None) -> Dict[str, Any]:
    """Parses the night plan created with 'calibrator_find.pro' into the
    individual runs as key of a dictionary, specified by the 'run_identifier'.
    If no match is found then it parses the whole night to 'run_identifier's
    or the 'default_key', respectively.

    Parameters
    ----------
    night_plan_path: Path
        The night plan, a (.txt)-file containing the observations for one
        or more runs
    run_identifier: str, optional
        The run-identifier that splits night plan into its runs
    night_identifier: str, optional
        The night-identifier by which the runs are split into the
        its nights.
    save_path: bool, optional
        If this is set to true then it saves the dictionary as
        'night_plan.yaml', Default is 'False'

    Returns
    -------
    night_dict: Dict
        A dict that contains the <default_search_param> as key and a list
        containing the sub lists 'sci_lst', 'cal_lst' and 'tag_lst'
    """
    night_plan_path = Path(night_plan_path)
    if night_plan_path.exists():
        with open(Path(night_plan_path), "r+") as night_plan:
            lines = night_plan.readlines()
    else:
        raise FileNotFoundError(f"File {night_plan_path.name} was not found/does not exist!")

    runs = {}
    for run_id, run in _get_file_section(lines, run_identifier).items():
        nights = {}
        for night_id, night in _get_file_section(run, night_identifier).items():
            nights[night_id] = parse_groups(night)
        runs[run_id] = nights
    print(runs) 

    # if save_path:
        # yaml_file_path = Path(save_path) / "night_plan.yaml"
        # with open(yaml_file_path, "w+") as night_plan_yaml:
            # yaml.safe_dump(night_plan_dict, night_plan_yaml)
        # print(f"Created {yaml_file_path}")
    # return night_plan_dict


if __name__ == "__main__":
    data_dir = Path(__file__).parent.parent / "tests/data" / "night_plan_small.txt"
    print(parse_night_plan(data_dir))
