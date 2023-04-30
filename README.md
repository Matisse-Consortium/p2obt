# P2obp

<!-- Project Shields -->
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
![Lifecycle: development](https://img.shields.io/badge/lifecycle-development-blue.svg)

<!-- Project Status -->
## Project Status
_Under maintenance/In development_

<!-- About The Project -->
## About the Project
The Phase 2 OB Pipeline (p2obp) has been made to streamline/automate
the process of MATISSE observation preparation on p2.

* For more infomration on the inner workings see [Features](#features).
* For upcoming features or to report bugs see the **issues**.
* To get started see [Installation](#installation) and [Usage](#usage).

<!-- Getting Started -->
## Installation
To install `p2obp` simple use the commands
```
git clone 
cd p2obp
pip install .
```
or
```
pip install git+
```

### Optional
* R. van Boekel's `calibrator_find.pro` IDL software for calibrator finding
(optional) and `night_plan` creation (which can then used to feed the parser and
the ob-creation).

<!-- Features -->
## Features
The full pipeline can cover the following:<br>

* [Night Plan Parsing](#night-plan-parsing)
* [OB-Creation](#ob-creation)
* [Upload](#upload)

### Night-Plan Parsing
Night/observation plans ((.txt)-files) created with `calibrator_find.pro` by R. van Boekel (optional)
can be parsed into dictionaries to be used by other parts of the program.<br><br>
The parser
* looks for the **runs** and splits them into individual keys/sections.
* looks for the **nights** and then splits them into keys/sections as well.
* ignores comments and other things in between the lines.
* in conjunction with the `create_obs`-function, can autodetect many things
(c.f., [Formatting Guidelines](#formatting-guidelines))
The **night** sections are ended as soon as a line containing the **cal_find**
software name is detected.<br>

#### Formatting Guidelines
In order to even better utilise the parser it is helpful to adhere to some
guidlines while writting the night/observation plans.<br>
These are outlined in the following:

##### Run Names
The parser will only identify sections of a file as a run, that contain a line
starting with **run**.<br>
If none of them are detected then the whole file will be identified as one run and
attributed as **full_run**.<br>
Additionally, if the run name has a certain shape/format, then the `create_obs` script
can automatically determine the following things about the run:<br>
* The **array configuration** (*UTs, small, medium, large, extended*)
* The **operational mode** (*MATISSE, GRA4MAT or BOTH*)
* The **resolution** (*LOW/LR, MED/MEDIUM/MR or HIGH/HR*)
* The **program id** (and by this the container id on p2)

For the parsing to work neither the order or capitalization of the above information
matters.<br>
Here is a few working examples:<br>
```
run 2, 111.253T.002 - UTs, both, med
run 3, 109.2313.003 = 0109.C-0413(C), ATs large array MR
```
This would upload both the MATISSE standalone as well as the
GRA4MAT obs to the run2 (111.253T.002) on p2
in medium resolution for the UTs array configuration.<br><br>

##### Night Names
The parser can also identify individual nights that are contained within a run by
lines starting with **night** that are followed up by some block containing
science targets and calibrators. This means, there is no need to avoid the word night
to, for instance, give a more detailed description in the night plan for the observers.<br>
Here are a few examples that are parsed properly:
```
obs-night 1 (27 dec): twilight + 0.5bn
Night 1 - 27 December
night 1:  1.6h1, formal duration our slot = 08:53 - 16:57 LST  =  23:38 - 07:42 UTC  =  01:38 - 09:42 CEST
night 2, June 6:
```

##### Block Identifiers

##### Example
Here is an example of a full `night_plan`:
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

### OB-Creation
The ob-creation scripts (for multiple obs `create_obs` or for singular obs `create_ob`)
* Sorts them into folders in the order given (either CAL-SCI or SCI-CAL or CAL-SCI-CAL)<br>

### Upload

<!-- USAGE EXAMPLES -->
## Usage
The `p2obp` software makes three functions directly available to the user:
* The `query` script, that gives the user direct information on the target.
* The `create_ob` script, which makes singular ob-creation and upload possible.
* The `create_obs` script, which has the capability of fully automated
night/observation plan parsing and from this ob creation and upload. Alternatively, it
also provides the same automated (local (.obx)) creation and upload for manual input.<br><br>
For examples of the above scripts' usage, see the `examples/`-directory.<br>

## Resources
* [Phase 2 API](https://www.eso.org/sci/observing/phase2/p2intro/Phase2API.html)
* [User-contributed software ESO](https://www.eso.org/sci/observing/phase2/p2intro/Phase2API/ApiContributedSoftware.html)

<!-- License -->
# License
Distributed under the MIT License. See LICENSE for more information.

<!-- Credit -->
# Credit
## Used Code by
* T. Bierwirth (`p2api`)
* R. van Boekel (`calibrator_find.pro`, not included in this repo and optional)

## Inspiration
* M. Pruemm whose `loadobxy` script inspired the
`p2obp.backend.upload` andj `p2obp.backend.compose` scripts.
* J. Varga whose `MATISSE_create_OB_2.py` and `query_CDS.py` scripts inspired
the `p2obp.backend.query` and `p2obp.backend.compose` scripts.

## Contributors
* [M. B. Scheuck](https://www.github.com/MBSck/)
