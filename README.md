# P2obp

<!-- Project Shields -->
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
![Lifecycle: broken](https://img.shields.io/badge/lifecycle-broken-red.svg)

<!-- Project Status -->
## Project Status
_In a working state/Under maintenance/development_

<!-- About The Project -->
## About the Project
The Phase 2 OB Pipeline (p2obp) has been made to streamline/automate the whole process of MATISSE observation preparation

* For more info see [Features](#features)
* For upcoming features or bugs see the **issues** of this project
* See [Installation](#installation) and [Usage](#usage)

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
All of the following scripts, which are executed by `p2obp.py` are also usable individually and have more extensive usage information in their file docstrings.<br>
The full pipeline is made up of the following scripts:<br>

* [Night Plan Parsing](#night-plan-parsing): `parser.py`
* [OB-Creation](#ob-creation): `creator.py`
* [P2ui Access](#p2ui-access): `uploader.py`

### Night-Plan Parsing
Parses night plans created with `calibrator_find.pro` by R. van Boekel (optional).<br>
The format is based on the following `night_plan`-excerpt (Comments in between the lines are ignored, the parser looks for the **run**, **night** and **calibrator** keyword to define the individual sections and subsections):
```
run 3, 109.2313.003 = 0109.C-0413(C), ATs large array

Jun 6, formal night duration:  LST 11:40 - 22:21  =  10:41 h = 641 min
                                   23:21 - 09:59 UTC =  01:21 - 11:59  CEST
00:00 LST = 11:41 UTC = 13:41 CEST

Jun 5, 1.0n   11:40 - 22:21 LST = 23:21 - 09:59 UTC = evening twilight + 01:21 - 11:59 CEST + morning twilight
Jun 6, 1.2h2  start after 0.4n = 11:40 + 04:16 = 15:56 to end of night = 03:37 - 09:59 UTC = 05:37 - 11:59 + morning twilight
Jun 7, 1.2h2  start after 0.4n = 11:40 + 04:16 = 15:56 to end of night = 03:37 - 09:59 UTC = 05:37 - 11:59 + morning twilight

night 2, June 6:
LST   source            coordinates                      L        N      K      V         SpT    diam   airm.   time  comment
                        RA (J2000)   dec (J2000)      [Jy]     [Jy]  [mag]  [mag]               [mas]          [min]

# If we get a full night, start here:
11:40 cal_LN_HD138538   15 36 43.222  -66 19 01.33    65.7     10.6          4.11     K1.5III    2.47    1.70     30
12:10 HD 104237         12 00 05.081  -78 11 34.56     8.6     13.4   4.59                               1.69     30  MR

12:40 HD 100546         11 33 25.437  -70 11 41.24     6.5     59.9   5.42                               1.47     30  MR
13:10 cal_LN_HD102839   11 49 56.614  -70 13 32.85    43.9      7.3          4.99        G6Ib    2.02    1.49     30  Check for variability of star

13:40 cal_L_HD96918     11 08 35.390  -58 58 30.13    67.2     11.0          3.92       G0Ia0    2.39    1.41     30
14:10 HD 98922          11 22 31.674  -53 22 11.46    16.6     31.4   4.28                               1.40     30  MR
14:40 cal_N_HD102461    11 47 19.141  -57 41 47.39    80.4     13.2          5.44       K5III    2.97    1.46     30

...

calibrator_find,zoom=3,duration=30,delay='large',max_d_am=0.2,max_d_az=90,minF10=5,max_diam=3,do_cal=0,LN=1,'HD 100546',LST='12:40',cal='HD102839',/print
calibrator_find,zoom=3,duration=30,delay='large',max_d_am=0.2,max_d_az=90,minF10=5,max_diam=3,do_cal=1,LN=0,'HD 98922',LST='13:40',cal='HD96918',/print
calibrator_find,zoom=3,duration=30,delay='large',max_d_am=0.2,max_d_az=90,minF10=5,max_diam=3,do_cal=0,LN=0,'HD 98922',LST='14:10',cal='HD102461',/print
...
```
Into a dictionary, which can be saved into a `night_plan.yaml`. Example:
```
run 3, 109.2313.003 = 0109.C-0413(C), ATs large array:
  'night 2, June 6:':
    CAL:
    - - HD138538
    - - HD102839
    - - HD96918
      - HD102461
    ...
    SCI:
    - HD 104237
    - HD 100546
    - HD 98922
    - HD 142666
    ...
    TAG:
    - - LN
    - - LN
    - - L
      - N
    ...
```

### OB-Creation
* Creates (.obx)-files from either manual input list or a `night_plan.yaml`
* Sorts them into folders in the order given (either CAL-SCI or SCI-CAL or CAL-SCI-CAL)<br>
Example of automatically generated `creator.log`-file:
```
2022-11-13 04:26:59,703 - Creating OBs for 'run 3, 109.2313.003 = 0109.C-0413(C), ATs large array'
2022-11-13 04:26:59,704 - Creating folder: 'run3'
2022-11-13 04:26:59,704 - Creating folder: 'night2_June6', and filling it with OBs
2022-11-13 04:27:00,864 - Created OB SCI-HD 104237
2022-11-13 04:27:01,428 - Created OB SCI-HD 100546
2022-11-13 04:27:02,030 - Created OB SCI-HD 98922
...
```

### P2ui Access
* Uploads the folders, containing the OBs, to the p2ui environment
* Generates finding charts for the individual OBs and then verifies them

<!-- Getting Started -->
## Installation
### Prerequisites
The software will raise an error if any of the following cannot be imported (scripts need to be put in `lib/`):
* J. Varga's `MATISSE_create_OB_2.py` automated (.obx)-template creation script
* J. Varga's `query_CDS.py` querying script

### Dependencies
Install the rest of the dependencies via the `requirements.txt` (as this is a semi-package) with:
```
pip install -r requirements.txt
```

### Optional
* R. van Boekel's `calibrator_find.pro` IDL software for calibrator finding (optional) and `night_plan` creation

<!-- USAGE EXAMPLES -->
## Usage
...

## Ressources
* [Phase 2 API](https://www.eso.org/sci/observing/phase2/p2intro/Phase2API.html)
* [User-contributed software ESO](https://www.eso.org/sci/observing/phase2/p2intro/Phase2API/ApiContributedSoftware.html)

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
* [M. B. Scheuck](https://www.github.com/MBSck/)
