from pathlib import Path
from typing import Dict, List, Optional

from .utils import prompt_user


# TODO: Make parser accept more than one calibrator block for one night, by
# checking if there are integers for numbers higher than last calibrator and
# then adding these


def parse_operational_mode(run_name: str) -> str:
    """Parses the run's used instrument from string containing it,
    either MATISSE or GRA4MAT.

    If no match can be found it prompts the user for
    manual operational mode input.

    Parameters
    ----------
    run_name : str, optional
        The name of the run.

    Returns
    -------
    operational_mode : str
        Either "MATISSE" or "GRA4MAT".
    """
    if "GRA4MAT" in run_name:
        operational_mode = "gr"
    elif "MATISSE" in run_name:
        operational_mode = "st"
    else:
        operational_mode = prompt_user("instrument",
                                       ["MATISSE", "GRA4MAT"])
    return operational_mode


def parse_array_config(run_name: Optional[str] = None) -> str:
    """Parses the array configuration from string containing it.

    If no run name is specified or no match can be found
    it prompts the user for manual configuration input.

    Parameters
    ----------
    run_name : str, optional
        The name of the run.

    Returns
    -------
    array_configuration : str
        Either "UTs", "small", "medium", "large" or "extended".
    """
    at_configs = ["ATs", "small", "medium", "large", "extended"]
    if run_name:
        if "UTs" in run_name:
            array_configuration = "UTs"
        elif any(config in run_name for config in at_configs):
            if "small" in run_name:
                array_configuration = "small"
            elif "medium" in run_name:
                array_configuration = "medium"
            elif "large" in run_name:
                array_configuration = "large"
            else:
                array_configuration = "extended"
    else:
        array_configuration = prompt_user("array_configuration",
                                          ["UTs"]+at_configs[1:])
    return array_configuration


def parse_run_resolution(run_name: str) -> str:
    """Parses the run's resolution from string containing it.

    If no match can be found it prompts the user for
    manual resolution input.

    Parameters
    ----------
    run_name : str, optional
        The name of the run.

    Returns
    -------
    resolution : str
        Either "LOW", "MED" or "HIGH".
    """
    if "LR" in run_name:
        resolution = "LOW"
    elif "MR" in run_name:
        resolution = "MED"
    elif "HR" in run_name:
        resolution = "HIGH"
    else:
        resolution = prompt_user("resolution", ["LOW", "MED", "HIGH"])
    return resolution


def parse_run_prog_id(run_name: str) -> str:
    """Parses the run's resolution from string containing it.

    If no match can be found it prompts the user for
    manual resolution input.

    Parameters
    ----------
    run_name : str, optional
        The name of the run.

    Returns
    -------
    run_prog_id : str
        The run's program id in the form of
        <period>.<program>.<run> (e.g., 110.2474.004).
    """
    run_prog_id = None
    for element in run_name.split():
        if len(element.split(".")) == 3:
            run_prog_id = element
            break

    if run_prog_id is None:
        print("Run's program id could not be automatically detected!")
        run_prog_id = input("Please enter the run's id in the following form"
                            " (<period>.<program>.<run> (e.g., 110.2474.004)): ")
    return run_prog_id


# TODO: Write down how the nights need to be written down in the observing plan
def parse_night_name(night_name: str) -> str:
    """Automatically gets the night's date from a night key of
    the dictionary if the date it is included in the key.

    Parameters
    ----------
    night_key : str
        The dictionary's keys that describes a night.

    Returns
    -------
    night_name : str
        If night date in night then of the format <night>_<night_date> if not
        then <night>.
    """
    if "full" in night_name:
        return night_name

    night = night_name.split(":")[0].strip()
    date = night_name.split(":")[1].split(",")[0].strip()

    if len(night.split()) > 2:
        try:
            night, date = night.split(",")[:2]
        except ValueError:
            return night

    return "_".join([''.join(night.split()), ''.join(date.split())])\
        if date != '' else ''.join(night.split())


def parse_line(parts: str) -> str:
    """Parses a line from a night plan generated with the `calibrator_find`
    -tool and returns the objects name.

    Parameters
    ----------
    parts : str
        The line split into its individual components.

    Returns
    -------
    target_name : str
        The target's name.
    """
    target_name_cutoff = len(parts)
    for index, part in enumerate(parts):
        if index <= len(parts)-4:
            if part.isdigit() and parts[index+1].isdigit()\
               and "." in parts[index+2] and not index == len(parts)-4:
                target_name_cutoff = index
                break
    return " ".join(parts[1:target_name_cutoff])


def parse_groups(section: List) -> Dict:
    """Parses any combination of a calibrator-science target block
    into a dictionary containing the individual blocks' information.

    Parameters
    ----------
    section : list
        A section of a night plan (either a run or a night of a run).

    Returns
    -------
    data : dict
        The individual science target/calibrator group within a section.
        Can be for instance, "SCI-CAL" or "CAL-SCI-CAL" or any combination.
    """
    data = {}
    calibrator_labels = ["name", "order", "tag"]
    current_group, current_science_target = [], None

    for line in section:
        parts = line.strip().split()

        if not parts:
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

    # HACK: Remove all the empty parsings
    data = {key: value for key, value in data.items() if value}
    return data


def get_file_section(lines: List, identifier: str) -> Dict:
    """Gets the section of a file corresponding to the given identifier and
    returns a dict with the keys being the match to the identifier and the
    values being a subset of the lines list.

    Parameters
    ----------
    lines : list
        The lines read from a file.
    identifier : str
        The identifier by which they should be split into subsets.

    Returns
    --------
    subset : dict
        A dict that contains a subsets of the original lines.
    """
    indices, labels = [], []
    for index, line in enumerate(lines):
        if line.lower().startswith(identifier):
            indices.append(index)
            labels.append(line.strip())

    if not indices:
        indices, labels = [0], ["full_" + identifier]

    sections = [lines[index:] if index == indices[~0] else
                lines[index:indices[i+1]] for i, index in enumerate(indices)]
    return dict(zip(labels, sections))


# TODO: Add documentation for the night dict in the Returns
# TODO: Fix parsing of the first entry? -> Is parsed wrongly
# -> Check parsing generally.
def parse_night_plan(night_plan: Path,
                     run_identifier: Optional[str] = "run",
                     night_identifier: Optional[str] = "night"
                     ) -> Dict[str, Dict]:
    """Parses the night plan created with `calibrator_find.pro` into the
    individual runs as key of a dictionary.

    The parsed runs are specified by the 'run_identifier'. The parsed
    nights are specified by the 'night_identifier'.
    If no sections via the 'run_identifier' can be matched, then
    the full file will be parsed for nights and saved as 'full_run'.
    The same happens if no match via the 'night_identifier' can be
    made then it parses all within a run into 'full_night'.


    Parameters
    ----------
    night_plan : path
        The path to the night plan, a (.txt)-file containing
        the observations for one or more runs.
    run_identifier : str, optional
        The run-identifier by which the night plan is split into
        individual runs.
    night_identifier : str, optional
        The night-identifier by which the runs are split into the
        individual nights.

    Returns
    -------
    night_dict : dict
        A dictionary containing the individual runs, their nights
        and in those the individual observing blocks for the science targets
        with their associated calibrators.
    """
    night_plan = Path(night_plan)
    if night_plan.exists():
        with open(night_plan, "r+", encoding="utf-8") as night_plan:
            lines = night_plan.readlines()
    else:
        raise FileNotFoundError(
            f"File {night_plan.name} was not found/does not exist!")

    runs = {}
    for run_id, run in get_file_section(lines, run_identifier).items():
        nights = {}
        for night_id, night in get_file_section(run, night_identifier).items():
            night_content = parse_groups(night)

            # HACK: Only add nights that have content
            if night_content:
                nights[night_id] = night_content
        runs[run_id] = nights
    return runs


if __name__ == "__main__":
    path = Path("/Users/scheuck/Data/observations/P111/newest_plan.txt")
    print(parse_night_plan(path))
