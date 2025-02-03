"""
Create ob
==================

This script is meant to give an example on how to use the
the `create_ob`-function of p2obt to create a single ob and
either create it locally as an (.obx)-file or directly upload
it to ESO's P2-environment.
"""

# %%
from pathlib import Path

from p2obt import OPTIONS, create_ob

# %%
# Specify and create the path for the 'manualOBs' directory.
output_dir = Path("../assets") / "obs"
output_dir.mkdir(parents=True, exist_ok=True)

# %%
# Locally creating an (.obx)-file
# ------------------------
#
# Create a science target (.ob)
# Create an (.obx)-file for a science target for 'GRA4MAT'. If the
# 'ouput_dir' keyword is passed, an (.obx)-file gets created.
create_ob("HD 142666", "sci", "uts", mode="gr", output_dir=output_dir)

# %%
# Create an (.obx)-file for a calibrator for the UT-array configuration
# for the science target 'HD 142666' and for 'GRA4MAT', tagged as an "L"
# band calibrator.
create_ob(
    "HD 100920",
    "cal",
    "uts",
    sci_name="HD 142666",
    tag="L",
    mode="gr",
    output_dir=output_dir,
)

# %%
# NOTE: Change constraint settings
# Turbulence can be choosen from 10%, 30% or 70%. Default is 30%.
OPTIONS.constraints.turbulence = 70

# NOTE: Change sky-transparency settings. Can be choosen from 'photometric',
# 'clear', 'thin' and 'variable'. Default is 'clear'.
OPTIONS.constraints.transparency = "thin"

# %%
# Direct upload of an ob
# ------------------------
#
# If the 'container_id' keyword is passed then the (.obx)-file will be
# uploaded and if the 'connection'-keyword is none it will ask for your login
# data.
# For this example the ob will be uploaded to ESO's demo environment
# (https://www.eso.org/p2demo/home) to the subfolder "p2obt" of the
# run "60.A-9252(N) MATISSE".
# Tutorial server: username - '52052' , password - 'tutorial'
create_ob(
    "HD 100920",
    "cal",
    "uts",
    sci_name="HD 142666",
    mode="gr",
    container_id=3001786,
    server="demo",
    user_name="52052",
)
