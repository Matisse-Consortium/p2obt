.. _examples_ob_creation:

.. role:: bash(code)
   :language: bash

.. role:: python(code)
   :language: python

===========
OB Creation
===========

:bash:`p2obt` supports various ways of local or online (on P2) ob creation.
In addition to a single ob creating script (:ref:`Single OB Creation`), there is a fully automated pipeline
that can make multiple obs at once (:ref:`OB Creation Pipeline`).

------------------
Single OB Creation
------------------

This is meant to give some examples on how to use the
:func:`create_ob <p2obt.automate.create_ob>` for singular ob creation.

A full example script can be found in `examples/create_ob <https://github.com/MBSck/p2obt/blob/main/examples/create_single_ob.py>`_.

One can either locally create an (.obx)-file (see :ref:`Local Creation`) or
directly upload the content of a dictionary to the P2 environment (see :ref:`Direct Upload`).

Local Creation
==============

.. note::

  To locally create a science target (.obx)-file a :python:`Path` or :python:`str`
  must be provided for the :python:`ouput_dir` keyword. 

In the following an an (.obx)-file for a science target for
GRA4MAT setting will be created for the UTs.

.. code-block:: python

  create_ob("HD 142666", "sci", "uts",
            operational_mode="gr", output_dir=output_dir)


Similarly, for a calibrator an (.obx)-file for the UT-array configuration
for the science target :python:`"HD 142666"` and for GRA4MAT,
tagged as an L band calibrator can be created like this.

.. code-block:: python

  create_ob("HD 100920", "cal", "uts",
            sci_name="HD 142666", tag="L",
            operational_mode="gr", output_dir=output_dir)

.. note::

  The resolution for all other targets will be :python:`"low"`, but can be
  set via the options (see :ref:`options <p2obt.backend.options>` for a more comprehensive listing).

  .. code-block:: python

    OPTIONS.resolution.active = "med"

  This also applies for the :ref:`OB Creation Pipeline` as well.

  .. warning::

     The global resolution will be overwritten if a local catalog 
     is activated/queried and contains the target with a resolution specified.

     To avoid this set the overwrite option :python:`OPTIONS.resolution.overwrite`
     to :python:`True`.

     This will also be automatically set for service mode.


Direct Upload
=============

A direct upload to the P2 environment is also possible.

.. note:: 

  For this the :python:`container_id` keyword must be provided.

  Then the dictionary created will be directly uploaded and if the :python:`connection`-keyword
  is `:python:`None` it will ask for your login data otherwise it will directly connect.

Now an ob for the target :python:`"HD 100920"` as a calibrator for the science target
:python:`"HD 142666` will be directly created on the P2.

.. code-block:: python

  create_ob("HD 100920", "cal", "uts",
            sci_name="HD 142666", operational_mode="gr",
            container_id=3001786, server="demo", password="52052")

.. note::
  For this example the ob will be uploaded to ESO's demo environment
  (https://www.eso.org/p2demo/home) to the subfolder :bash:`p2obt` of the
  run :bash:`60.A-9252(N) MATISSE`.

--------------------
OB Creation Pipeline
--------------------

This is meant to give an example on how to use the
fully automated pipeline, :func:`create_obs <p2obt.automate.create_obs>`, of p2obt for ob-creation.
The full example script can be found in `examples/create_obs <https://github.com/MBSck/p2obt/blob/main/examples/create_obs.py>`_.

Manual Creation
===============

Now follows a step-by step guide for the usage of the script with manual input.

For the manual input, the user needs to specify multiple lists.
A :python:`science_targets` list is always required and optionally a :python:`calibrators` list can be given.
The science targets will be then assigned to the calibrators and one science target can have multiple calibrators (in a
one level nested list).

.. code-block:: python

  science_targets = ["Beta Leo", "HD 100453"]
  calibrators = [["HD100920", "HD173460"], "HD102964"]

.. note::
   
  There are two additional lists that can be specified. 
  The :python:`orders` lists specifies the order of the targets after upload, where :python:`"b"` stands
  for before and :python:`"a"` for after the science target. This results in either :bash:`SCI-CAL`, :bash:`CAL-SCI-CAL` or any combination.

  The other list that can be given is the :python:`tags` list, that specifies the calibrators' tags.
  The tags are 'L' for an L-band calibrator, 'N' for an N-band calibrator and "LN" for both bands.
  The default is "LN" for both.

  If the :python:`orders` and :python:`tags` lists are not provided by the user, they will be autofilled to have the same shape
  as the :python:`calibrators` list.

  .. code-block:: python

    orders = [["b", "a"], "a"]
    tags = [["L", "LN"], "N"]

These lists then need to be passed as a combined list :python:`manual_input` to the function:

.. code-block:: python

  manual_input = [sci_lst, cal_lst, tag_lst, order_lst]

.. note::

  With the :python:`resolutions` dictionary, one can manually set the resolution
  for specific targets as keys, with the resolution as values (either *low, med or high*).

  .. code-block:: python

    resolution = {"Beta Leo": "med"}

  .. warning::

     The global resolution as well as the :python:`resolution` dictionary 
     will be overwritten if a local catalog is activated/queried and contains the target.
     
     To avoid this set the overwrite option :python:`OPTIONS.resolution.overwrite`
     to :python:`True`.

     For more information see :ref:`options <p2obt.backend.options>`

The operational mode (either :python:`"gr"` for GRA4MAT or
:python:`"st"` for MATISSE-standalone specifies the obs' settings).
This will either upload the obs to a the specified container (keyword
:python:`container_id` on p2)

.. code-block:: python

  create_obs(manual_lst=manual_lst, operational_mode="both",
             resolution=resolution, container_id=3001786,
             server="demo", password="52052")

or make them locally as (.obx)-files, if an :python:`output_dir` is specified.

.. code-block:: python

  create_obs(manual_lst=manual_lst, operational_mode="both",
             resolution=res_dict, output_dir=output_dir)

.. note::

  For this example the ob will be uploaded to ESO's demo environment
  (https://www.eso.org/p2demo/home) to the subfolder :bash:`p2obt/` of the
  run :bash:`60.A-9252(N) MATISSE`.


Night Plan Based Creation
=========================

In addition to the manual creation, there is also a more automated way - The
core aspect of :bash:`p2obt` - the night plan parsing, automatic ob creation and upload.

.. note::

  For the specifics on the parser and examples for night plans
  see :ref:`Features - Night Plan Parsing <features>`.

After a night plan has been provided, the :func:`parse_night_plan <p2obt.backend.parse.parse_night_plan>`
function will parse this into chuncks of runs that have subsections for nights and in those
some sort of science target and calibrator(s) arrangements.

The code to create the (.obx)-files locally, is similar to before

.. code-block:: python

  create_obs(night_plan=night_plan,
             resolution=res_dict, output_dir=output_dir)

.. note::

   The parser, if the guidelines in :ref:`Features - Night Plan Parsing <features>` for
   the night plan are taken care of, can automatically determine the :python:`run_id`, 
   which is a run's :python:`container_id`, the :python:`array_configuration`, the 
   standard resolution :python:`OPTIONS.resolution.active` as well as the :python:`operational_mode`.
   
   If any of these cannot be automatically determined, the parser will prompt the user for
   each detected run and every not detected keyword.

   One can also directly provide a :python:`container_id`, then the automatically created
   obs will be uploaded to this container instead and possible :python:`run_id`'s will
   be ignored.

   Additionally, specifying an :python:`output_dir` will always overwrite the online creation.

and similarly for uploading the obs directly just omit the :python:`output_dir`.

.. code-block:: python

  create_obs(night_plan=night_plan, resolution=resolutions)
