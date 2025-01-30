import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# TODO: Implement this in the main function
# from .utils import prompt_user

# TODO: Make parser accept more than one calibrator block for one night, by
# checking if there are integers for numbers higher than last calibrator and
# then adding these


# TODO: Maybe substiute with match and cases?
def parse_operational_mode(line: str) -> str:
    """Parses the run's used instrument from string containing it,
    either MATISSE or GRA4MAT.

    If no match can be found it prompts the user for
    manual operational mode input.

    Parameters
    ----------
    run_name : str
        The name of the run.

    Returns
    -------
    operational_mode : str
        Either "MATISSE" or "GRA4MAT".
    """
    line = line.lower()
    if "gra4mat" in line:
        return "gr"
    if "matisse" in line:
        return "st"
    if "both" in line:
        return "both"
    return ""
    # operational_modes = ["MATISSE", "GRA4MAT", "Both"]
    # return prompt_user("instrument", operational_modes)


def parse_array_config(line: Optional[str] = None) -> str:
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
    if line is not None:
        line = line.lower()
        if "uts" in line:
            return "UTs"
        if any(config in line for config in at_configs):
            if "small" in line:
                return "small"
            if "medium" in line:
                return "medium"
            if "large" in line:
                return "large"
            if "extended" in line:
                return "extended"

    return ""
    # return prompt_user("array_configuration", ["UTs"] + at_configs[1:])


def parse_run_resolution(line: str) -> str:
    """Parses the run's resolution from string containing it.

    If no match can be found it prompts the user for
    manual resolution input.

    Parameters
    ----------
    run_name : str
        The name of the run.

    Returns
    -------
    resolution : str
        Either "LOW", "MED" or "HIGH".
    """
    line = line.lower()
    if any(res in line for res in ["lr", "low"]):
        return "LOW"
    if any(res in line for res in ["mr", "med", "medium"]):
        return "MED"
    if any(res in line for res in ["hr", "high"]):
        return "HIGH"
    return ""
    # return prompt_user("resolution", ["LOW", "MED", "HIGH"])


def parse_run_prog_id(run_name: str) -> str:
    """Parses the run's resolution from string containing it.

    If no match can be found it prompts the user for
    manual resolution input.

    Parameters
    ----------
    run_name : str
        The name of the run.

    Returns
    -------
    run_prog_id : str
        The run's program id in the form of
        <period>.<program>.<run> (e.g., 110.2474.004).
    """
    pattern = r"\b[\w\d]+\.[\w\d]+\.[\w\d]+\b"
    run_prog_id = re.findall(pattern, run_name)[0]

    if not run_prog_id:
        print("Run's program id could not be automatically detected!")
        run_prog_id = input(
            "Please enter the run's id in the following form"
            " (<period>.<program>.<run> (e.g., 110.2474.004)): "
        )
    return run_prog_id


def parse_night_name(night_name: str) -> str:
    """Automatically gets the night's date from a night key of
    the dictionary if the date it is included in the key.

    Parameters
    ----------
    night_name : str
        The dictionary's key for a night.

    Returns
    -------
    night : str
        The parsed night name.
    date : str, optional
        The parsed date.
    """
    if "full" in night_name:
        return night_name
    regex = r"(?i)night\s+(\d+).*?((\d{1,2}\s+(?:\w{3}|\w+))|(\w+\s+\d{1,2}))"
    day_month, month_day = "%d %b", "%B %d"

    match = re.search(regex, night_name)
    night = match.group(1) if match else None
    date_str = match.group(2) if match else None

    if date_str:
        try:
            date = datetime.strptime(date_str, day_month).date().strftime(month_day)
        except ValueError:
            try:
                date = datetime.strptime(date_str, month_day).date().strftime(month_day)
            except ValueError:
                date = None
    if night:
        return f"night {night} - {date}" if date else f"night {night}"
    return night_name


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
        if index <= len(parts) - 4:
            if (
                part.isdigit()
                and parts[index + 1].isdigit()
                and "." in parts[index + 2]
                and not index == len(parts) - 4
            ):
                target_name_cutoff = index
                break
    return " ".join(parts[1:target_name_cutoff])


# TODO: Make this more robust, it sometimes parses the calibrators not correctly (too long of the name)
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
    data, op_mode, array, res = [], "", "", ""
    calibrator_labels = ["name", "order", "tag"]
    current_group = {"cals": []}

    for line in section:
        parts = line.strip().split()

        if not parts:
            if current_group.get("name", None) is not None:
                data.append(current_group)

            current_group = {"cals": []}
            continue

        if line.startswith("#") or not line[0].isdigit():
            op_mode = parse_operational_mode(line)
            array = parse_array_config(line)
            res = parse_run_resolution(line)
            continue

        obj_name = parse_line(parts)
        if obj_name.startswith("cal_"):
            tag = obj_name.split("_")[1]
            order = "b" if current_group.get("name", None) is None else "a"
            calibrator = dict(
                zip(calibrator_labels, [obj_name.split("_")[2], order, tag])
            )
            current_group["cals"].append(calibrator)
        else:
            current_group["name"] = obj_name
            current_group["op_mode"] = op_mode
            current_group["array"] = array
            current_group["res"] = res
            op_mode, array, res = "", "", ""

    return [entry for entry in data if entry["cals"]]


def parse_file_section(lines: List, identifier: str) -> Dict:
    """Parses the section of a file that corresponds to the given identifier
    and returns a dict with the keys being the match to the identifier and
    the values being a subset of the lines list.

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

    sections = [
        lines[index:] if index == indices[~0] else lines[index : indices[i + 1]]
        for i, index in enumerate(indices)
    ]
    return dict(zip(labels, sections))


def parse_night_plan(
    night_plan: Path,
    run_identifier: Optional[str] = "run",
    night_identifier: Optional[str] = "night",
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
        raise FileNotFoundError(f"File {night_plan.name} was not found/does not exist!")

    runs = {}
    for run_id, run in parse_file_section(lines, run_identifier).items():
        nights = {}
        for night_id, night in parse_file_section(run, night_identifier).items():
            night_content = parse_groups(night)

            if night_content:
                nights[night_id] = night_content

        runs[run_id] = nights
    # TODO: Raise error here if the parsed night plan is empty and suggest adding a white line at the end
    return runs
