# P2obp

<!-- Project Shields -->
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
![Lifecycle: broken](https://img.shields.io/badge/lifecycle-maturing-red.svg)

<!-- Project Status -->
## Project Status
_In a working state/Under maintenance/development_

<!-- About The Project -->
## About the Project
The Phase 2 OB Pipeline (p2obp) has been made to streamline/automate the whole process of MATISSE observation preparation

> For more info see [Features](#features)
> For upcoming features or bugs see the *issues* of this project
> See [Installation](#installation) and [Getting Started](#getting-started)

<!-- Table of Contents -->
## Table of Contents
* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [Ressources](#ressources)
* [License](#license)
* [Credit](#credit)

<!-- Features -->
## Features
### Parsing
Parses night plans created with `calibrator_find.pro` by R. van Boekel (optional) into a `night_plan.yaml`
Example of an (automatically) generated `night_plan.yaml`:
``````
run 4, 109.2313.004 = 0109.C-0413(C), ATs medium array:
  'night 1, September 24:':
    CAL:
    - - HD27482
    SCI:
    - V892 Tau
    TAG:
    - - LN
  'night 2, September 25:':
    CAL:
    - - HD27482
    SCI:
    - AB Aur
    TAG:
    - - LN
run 6, 109.2313.006 = 0109.C-0413(C), UTs:
  'night 1, September 16:':
    CAL:
    - - HD17361
    - - HD17361
    SCI:
    - V892 Tau
    - V892 Tau
    TAG:
    - - LN
    - - LN
  'night 2, September 17:':
    CAL:
    - - HD26526
    - - HD26526
    SCI:
    - AB Aur
    - AB Aur
    TAG:
    - - LN
    - - LN
``````

### OB-creation
* Creates (.obx)-files from either manual input list or a `night_plan.yaml`
* Sorts them into folders into the order as given (eiter CAL-SCI or SCI-CAL or CAL-SCI-CAL)

### P2ui Access
* Uploades the folders containing the OBs to the p2ui environment.
* Generates finding charts for the OBs and verifies them

<!-- Getting Started -->
## Installation
### Prerequisites
The software will raise an error if any of the following cannot be imported (scripts need to be put in the 'lib'-folder):
* J. Varga's `MATISSE_create_OB_2.py` automated (.obx)-template creation script
* J. Varga's `query_CDS.py` querying script

### Dependencies
Install the rest of the dependencies via the `requirements.txt` (as this is a semi-package)

### Optional
* R. van Boekel's `calibrator_find.pro` IDL software for calibrator finding (optional) and `night_plan` creation

<!-- USAGE EXAMPLES -->
## Usage
...

## Ressources
* [Phase 2 API](#https://www.eso.org/sci/observing/phase2/p2intro/Phase2API.html)
* [User-contributed software ESO](#https://www.eso.org/sci/observing/phase2/p2intro/Phase2API/ApiContributedSoftware.html)

<!-- License -->
# License
Distributed under the MIT License. See LICENSE.txt for more information.

<!-- Credit -->
# Credit
## Used Code by
* M. Pruemm (`loadobx.py`)
* T. Bierwirth (`p2api`)
* J. Varga (`MATISSE_create_OB_2.py` and `query_CDS.py`, not included in this repo)
* R. van Boekel (`calibrator_find.pro`, not included in this repo and optional)

## Contributors
* [M. B. Scheuck](#https://www.github.com/MBSck/)
