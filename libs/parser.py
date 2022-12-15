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
# TODO: Add order with "a" for "after" and "b" for "before"
# TODO: Make parser accept more than one calibrator block for one night, by
# checking if there are integers for numbers higher than last calibrator and
# then adding these

# TODO: Think about making the parsing work differently, check what readlines
# accept -> Make similar to loadbobx, readblock and so...
import os
import yaml

from pathlib import Path
from typing import Dict, List, Optional

from utils import contains_element


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


def _get_targets_calibrators_tags(lines: List):
    """Gets the info for the SCI, CAL and TAGs from the individual lines

    Parameters
    -----------
    lines: List
        The lines to be parsed

    Returns
    -------
    Dict:
        A dictionary that contains the SCI, CAL and TAG lists
    """
    line_start = [index for index, line in enumerate(lines) if line[0].isdigit()][0]
    line_end = [index for index, line in enumerate(lines)\
                if line.startswith("calibrator_find")][0]
    lines = ['' if line == '\n' else line for line in lines[line_start:line_end]]

    sci_lst, cal_lst, tag_lst  = [], [[]], [[]]
    double_sci, counter = False, 0

    for index, line in enumerate(lines):
        try:
            if ((line == '') or (not line.split()[0][0].isdigit()))\
               and (lines[index+1].split()[0][0].isdigit()):
                counter += 1
                cal_lst.append([])
                tag_lst.append([])

            else:
                line = line.split(' ')
                if (line[0][0].isdigit()) and (len(line) > 2)\
                   and (len(line[0].split(":")) == 2):
                    # NOTE: Gets the CAL
                    if "cal_" in line[1]:
                        temp_cal = line[1].split("_")
                        cal_lst[counter].append(temp_cal[2])
                        tag_lst[counter].append(temp_cal[1])

                        if double_sci:
                            cal_lst.append([])
                            tag_lst.append([])
                            cal_lst[counter+1].append(temp_cal[2])
                            tag_lst[counter+1].append(temp_cal[1])
                            double_sci = False
                    else:
                        # NOTE: Fixes the case where one CAL is for two SCI
                        if (index != len(lines)-3):
                            try:
                                if lines[index+1][0][0].isdigit() and\
                                   not ("cal_" in lines[index+1].split(' ')[1]) and\
                                   lines[index+2][0][0].isdigit():
                                    double_sci = True
                            except:
                                pass

                        # NOTE: Gets the SCI
                        if line[3] != '':
                            sci_lst.append((line[1]+' '+line[2]+' '+line[3]).strip())
                        else:
                            sci_lst.append((line[1]+' '+line[2]).strip())
        except:
            pass

    return {"SCI": sci_lst, "CAL": cal_lst, "TAG": tag_lst}


def parse_night_plan(night_plan_path: Path,
                     run_identifier: Optional[str] = "run",
                     sub_identifier: Optional[str] = "night",
                     save_path: Optional[Path] = "") -> Dict[str, List]:
    """Parses the night plan created with 'calibrator_find.pro' into the
    individual runs as key of a dictionary, specified by the 'run_identifier'.
    If no match is found then it parses the whole night to 'run_identifier's
    or the 'default_key', respectively.

    Parameters
    ----------
    night_plan_path: Path
        The night plan of the '.txt'-file format to be read and parsed
    run_identifier: str, optional
        Set to default identifier that splits the individual runs into keys of
        the return dict as 'run'
    sub_identifier: str, optional
        Set to default sub identifier that splits the individual runs into the
        individual nights. That is, in keys of the return dict as 'night'
    save_to_file: bool, optional
        If this is set to true then it saves the dictionary as
        'night_plan.yaml', Default is 'False'

    Returns
    -------
    night_dict: Dict
        A dict that contains the <default_search_param> as key and a list
        containing the sub lists 'sci_lst', 'cal_lst' and 'tag_lst'
    """
    night_plan_dict = {}
    night_plan_path = Path(night_plan_path)
    if night_plan_path.exists():
        with open(Path(night_plan_path), "r+") as night_plan:
            lines = night_plan.readlines()
    else:
        raise FileNotFoundError(f"File {Path(night_plan_path)} was not found/does not exist!")

    runs = _get_file_section(lines, run_identifier)

    for label, section in runs.items():
        subsection_dict = _get_file_section(section, sub_identifier)

        nights = {}
        for sub_label, sub_section in subsection_dict.items():
            if contains_element(sub_section, "cal_"):
                nights[sub_label] = _get_targets_calibrators_tags(sub_section)

        night_plan_dict[label] = nights

    if save_path:
        yaml_file_path = Path(save_path) / "night_plan.yaml"
        with open(yaml_file_path, "w+") as night_plan_yaml:
            yaml.safe_dump(night_plan_dict, night_plan_yaml)
        print(f"Created {yaml_file_path}")
    return night_plan_dict


# TODO: Parser is broken right now, fix!
if __name__ == "__main__":
    data_dir = Path().home() / "Data" / "observations" / "P110"
    file_path = "AT_run4_p110_MATISSE_YSO_observing_plan_backup.txt"
    parse_night_plan(data_dir / file_path, save_path=data_dir)

