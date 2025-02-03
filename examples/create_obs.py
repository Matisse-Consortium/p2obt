"""
Automatic ob creation pipeline
==============================

This is meant to give an example on how to use the
fully automated pipeline of p2obt for ob-creation, namely the script
"create_obs".
"""
from pathlib import Path

from p2obt import OPTIONS, create_obs

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

# NOTE: With the resolution_dict, one can manually set the resolution
# for specific targets as keys, with the resolution as values.
# The standard resolution is 'low'.
res_dict = {"Beta Leo": "med"}

# NOTE: Change constraint settings
# Turbulence can be choosen from 10%, 30% or 70%. Default at 10%
OPTIONS.constraints.turbulence = 30

# NOTE: Change sky-transparency settings. Can be choosen from 'photometric',
# 'clear', 'thin' and 'variable'. Default at 'thin'.
OPTIONS.constraints.transparency = "clear"

# NOTE: The operational mode (either 'gr' for 'GRA4MAT' or 'st' for
# 'MATISSE'-standalone specifies the obs' settings).
# This will either upload the obs to a the specified container (keyword
# 'container_id' on p2) or make them locally, if an 'output_dir' is
# specified.
create_obs(targets=sci_lst, calibrators=cal_lst,
           orders=order_lst, tags=tag_lst,
           operation_mode="gr",
           resolution=res_dict, output_dir=output_dir,
           server="demo", user_name="52052")
