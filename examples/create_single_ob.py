"""
Create singular ob
==================

This script is meant to give an example on how to use the
the `create_ob`-function of p2obp to create a single ob and
either create it locally as an (.obx)-file or directly upload
it to ESO's P2-environment.
"""
# %%
from pathlib import Path

from p2obp import OPTIONS, create_ob

# %%
# The path in which the 'manualOBs'-directory will be created.
output_dir = Path("../assets") / "obs"

# Create the folder if it does not exist
if not output_dir.exists():
    output_dir.mkdir(parents=True)

# %%
# Locally creating an (.obx)-file
# ------------------------
#
# Create a science target (.ob)
# Create an (.obx)-file for a science target for 'GRA4MAT'. If the
# 'ouput_dir' keyword is passed, an (.obx)-file gets created.
create_ob("HD 142666", "sci", "uts",
          operational_mode="gr", output_dir=output_dir)

# %%
# Create an (.obx)-file for a calibrator for the UT-array configuration
# for the science target 'HD 142666' and for 'GRA4MAT', tagged as an "L"
# band calibrator.
create_ob("HD 100920", "cal", "uts",
          sci_name="HD 142666", tag="L",
          operational_mode="gr", output_dir=output_dir)

# %%
# Changing the global resolution settings
# ------------------------
#
# The standard resolution for all targets will be 'low', but can be
# changed via the following.
OPTIONS["resolution"] = "med"

# NOTE: Change constraint settings
# Turbulence can be choosen from 10%, 30% or 70%. Default is 70%.
OPTIONS["constraints.turbulence"] = 30

# NOTE: Change sky-transparency settings. Can be choosen from 'photometric',
# 'clear', 'thin' and 'variable'. Default is 'thin'.
OPTIONS["constraints.transparency"] = "clear"

# %%
# Direct upload of an ob
# ------------------------
#
# If the 'container_id' keyword is passed then the (.obx)-file will be
# uploaded and if the 'connection'-keyword is none it will ask for your login
# data.
# For this example the ob will be uploaded to ESO's demo environment
# (https://www.eso.org/p2demo/home) to the subfolder "p2obp" of the
# run "60.A-9252(N) MATISSE".
# Tutorial server: username - '52052' , password - 'tutorial'
create_ob("HD 100920", "cal", "uts",
          sci_name="HD 142666", operational_mode="gr",
          container_id=3001786, server="demo",
          user_name="52052", password="tutorial")
