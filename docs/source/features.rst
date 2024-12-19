.. _features:

.. role:: bash(code)
   :language: bash

========
Features
========
The full pipeline can cover the following:

* Night Plan Parsing
* OB-Creation

.. note::

   For a guide on how to use the here described features and examples see :ref:`Getting Started - OB Creation <examples_ob_creation>`.

------------------
Night-Plan Parsing
------------------

Night/observation plans ((.txt)-files) created with the idl-tool :bash:`calibrator_find.pro` by R. van Boekel (optional)
can be parsed into dictionaries to be used by other parts of the program.
The parser

* looks for the **runs** and splits them into individual keys/sections (see :ref:`Run Names`).
* looks for the **nights** and then splits them into keys/sections as well (see :ref:`Night Names`).
* ignores comments and other things in between the lines and automatically creates the 
* in conjunction with the :func:`create_obs <p2obt.automate.create_obs>`-function, can autodetect many things (see :ref:`Formatting Guidelines`).

The **night** sections are ended as soon as a line containing the **cal_find**
software name is detected.

Formatting Guidelines
=====================

In order to even better utilise the parser it is helpful to adhere to some
guidlines while writting the night/observation plans.
These are outlined in the following:

.. note::

   The parser will only identify sections of a file as a run, that contain a line
   starting with **run** (optional)

   The parser will only identify sections of a file as a run, that contain a line
   starting with **run** (optional).

.. warning::
   :name: Important Notice
   
   In order for the parser to work within individual nights /runs, i.e., the individual
   observing blocks, the SCI-CAL (or CAL-SCI-CAL, SCI-CAL-SCI, or any combination) needs
   to be separated from the next (SCI-CAL, etc.) observing block by a white line or
   a comment (a line starting with #).
   In case for files that end on such an observation block, a white line should be added
   to ensure the proper functioning of the parser.


Run Names
---------

.. note::

   If no run is detected then the whole file will be identified as one run and
   attributed to be a **full_run**.

Additionally, if the run name has a certain shape/format, then the 
:func:`create_obs <p2obt.automate.create_obs>` function
can automatically determine the following things about the run:

* The **array configuration** (*UTs, small, medium, large, extended*)
* The **operational mode** (*MATISSE, GRA4MAT or BOTH*)
* The **resolution** (*LOW/LR, MED/MEDIUM/MR or HIGH/HR*)
* The **program id** (and by this the container id on p2)

.. note:: 

   The parser is insensitive to the order and capitalization of the above settings.

Here are some examples

.. admonition:: File Contents

   .. parsed-literal::

      run 2, 111.253T.002 - UTs, both, med
      run 3, 109.2313.003 = 0109.C-0413(C), ATs large array MR
   
This would upload both the MATISSE standalone as well as the
GRA4MAT obs to the run2 (111.253T.002) on p2 in medium resolution for the UTs array configuration.

Night Names
-----------

.. note::

   If no night is detected within a run then the whole run will be identified as one
   night and attributed to be a **full_night**.

The parser can also identify individual nights that are contained within a run by
lines starting with **night** that are followed up by some block containing
science targets and calibrators. This means, there is no need to avoid the word night
to, for instance, give a more detailed description in the night plan for the observers
at other locations.

Here are a few examples will be parsed properly:

.. admonition:: File Contents

   .. parsed-literal::

      obs-night 1 (27 dec): twilight + 0.5bn
      Night 1 - 27 December
      night 1:  1.6h1, formal duration our slot = 08:53 - 16:57 LST  =  23:38 - 07:42 UTC  =  01:38 - 09:42 CEST
      night 2, June 6:

.. note::

   If the above examples are not directly followed by a science target-calibrator block they may
   occur anywhere in the file and it will be parsed properly.

Night Plan Example
==================

.. admonition:: File Contents

   .. parsed-literal::

      run 3, 109.2313.003 = 0109.C-0413(C), ATs large array, MATISSE, LR

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

-----------
OB-Creation
-----------

The ob-creation scripts (for multiple obs :func:`create_obs <p2obt.automate.create_obs>`
or for singular obs :func:`create_ob <p2obt.automate.create_ob>`).
These scripts automatically...

* queries different catalogs (*simbad, gaia, tycho, 2mass, mdfc, and the local catalogs*).
* sort them into folders in the order given (either CAL-SCI or SCI-CAL or CAL-SCI-CAL) locally.
* sort them into containers during the upload, directly to P2.

For more details see the documentation or scripts in the `examples/ <https://github.com/MBSck/p2obt/tree/main/examples>`_ directory.
To add new local query targets add them to the :bash:`data/Extensive Target Information` excel sheet.
