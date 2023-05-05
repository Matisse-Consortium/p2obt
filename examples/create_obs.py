"""
Automatic ob creation pipeline
=========================

This is meant to give an example on how to use the
fully automated pipeline of p2obp for ob-creation, namely the script
"create_obs".
"""
from pathlib import Path

from p2obp import options, ob_creation

# NOTE: The path in which the 'manualOBs'-directory will be created
output_dir = Path("../assets/")

# NOTE: The science targets will be assigned to the calibrators
# and one science target can have multiple calibrators (in a
# nested list).
sci_lst = ["Beta Leo", "HD 100453"]
cal_lst = [["HD100920", "HD173460"], "HD102964"]

# NOTE: These lists specify the order. SCI-CAL, CAL-SCI-CAL
# or any combination as well as the calirators' tags. 'L', 'N'
# or 'LN'. By default they will be filled with 'a' (for after)
# and 'LN' and can be left empty.
order_lst = [["b", "a"], "a"]
tag_lst = [["L", "LN"], "N"]

# NOTE: To pass manual input to the program, make a list of lists.
manual_lst = [sci_lst, cal_lst, tag_lst, order_lst]

# NOTE: With the resolution_dict, one can manually set the resolution
# for specific targets as keys, with the resolution as values.
res_dict = {"Beta Leo": "med"}

# NOTE: The resolution for all other targets will be 'low', but can be
# set via the options.
options["resolution"] = "low"

# NOTE: The operational mode (either 'gr' for 'GRA4MAT' or 'st' for
# 'MATISSE'-standalone specifies the obs' settings).
# This will either upload the obs to a the specified container (keyword
# 'container_id' on p2) or make them locally, if an 'output_dir' is
# specified.
ob_creation(manual_lst=manual_lst, operational_mode="both",
            resolution=res_dict, output_dir=output_dir)
