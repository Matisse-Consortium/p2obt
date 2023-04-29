"""This script is meant to give an example on how to use the
the "create_ob" feature of p2obp to create a single ob.
"""
from pathlib import Path

from p2obp import options, create_ob

# NOTE: The path in which the 'manualOBs'-directory will be created.
output_dir = Path("../assets/")

# NOTE: Create an (.obx)-file for a science target for 'GRA4MAT'. If the
# 'ouput_dir' keyword is passed, it an (.obx)-file gets created.
create_ob("HD 142666", "sci", "uts",
          operational_mode="gr", output_dir="assets/")

# NOTE: Create an (.obx)-file for a calibrator for the UT-array configuration
# for the science target 'HD 142666' and for 'GRA4MAT'.
cal_ob = create_ob("HD 100920", "cal", "uts", sci_name="HD 142666",
                   operational_mode="gr", output_dir="assets/")

# NOTE: The resolution for all other targets will be 'low', but can be
# set via the options.
options["resolution"] = "low"

# NOTE: If the 'container_id' keyword is passed then the (.obx)-file will be
# uploaded and if the 'connection'-keyword is none it will ask for your login
# data.
# TODO: Add here the container id to test (the MATISSE-one) as well
# as the login data for the demo account
cal_ob = create_ob("HD 100920", "cal", "uts", sci_name="HD 142666",
                   operational_mode="gr", container_id=0, server="demo")
