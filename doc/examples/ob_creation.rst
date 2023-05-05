.. role:: python(code)
   :language: python

===========
OB Creation
===========

------------------
Single OB Creation
------------------

This is meant to give an example on how to use the
:func:`create_ob <p2obp.automate.create_ob>` for singular ob creation
The full example script can be found in `examples/create_ob <https://github.com/MBSck/p2obp/blob/main/examples/create_ob.py>`_.

One can either locally create an (.obx)-file (see :ref:`Local Creation`) or
directly upload the content of a dictionary to the P2 environment (see :ref:`Direct Upload`).

Local Creation
--------------

To locally create a science target (.obx)-file pass a :python:`Path` or :python:`str`
as the :python:`ouput_dir` keyword. In the following an an (.obx)-file
for a science target for GRA4MAT setting will be created for the UTs.

.. code-block:: python

  create_ob("HD 142666", "sci", "uts",
            operational_mode="gr", output_dir=output_dir)


Similarly, for a calibrator an (.obx)-file for the UT-array configuration
for the science target HD 142666 and for GRA4MAT, tagged as an L band calibrator
can be created like this:

.. code-block:: python

  create_ob("HD 100920", "cal", "uts",
            sci_name="HD 142666", tag="L",
            operational_mode="gr", output_dir=output_dir)

.. note::

  The resolution for all other targets will be :python:`"low"`, but can be
  set via the options (see :ref:`options <p2obp.backend.options>` for a more comprehensive listing).

  .. code-block:: python

    options["resolution"] = "med"

  This also applies for the :ref:`OB Creation Pipeline` as well.

  .. warning::

     The global resolution will be overwritten if a local catalog 
     (see :ref:`options <p2obp.backend.options>`) is activated/queried and contains
     the target and the overwrite option :python:`options["resolution.overwrite"]`
     is set to :python:`False` (standard setting).


Direct Upload
-------------

There is also functionality for a direct upload to the P2 environment.
If the :python:`container_id` keyword is passed then the dictionary created 
will be directly uploaded and if the :python:`connection`-keyword is `:python:`None`
it will ask for your login data.

.. note::
  For this example the ob will be uploaded to ESO's demo environment
  (https://www.eso.org/p2demo/home) to the subfolder :python:`p2obp` of the
  run :python:`60.A-9252(N) MATISSE`.

.. code-block:: python

  create_ob("HD 100920", "cal", "uts",
            sci_name="HD 142666", operational_mode="gr",
            container_id=3001786, server="demo", password="52052")

--------------------
OB creation pipeline
--------------------

This is meant to give an example on how to use the
fully automated pipeline, :func:`create_obs <p2obp.automate.create_obs>`, of p2obp for ob-creation.
The full example script can be found in `examples/create_obs <https://github.com/MBSck/p2obp/blob/main/examples/create_obs.py>`_.

Manual Creation
---------------

Now follows a step-by step guide for the usage of the script with manual input.

For the manual input, the user needs to specify multiple lists.
A :python:`science_targets` list is always required and optionally a :python:`calibrators` list can be given.
The science targets will be then assigned to the calibrators and one science target can have multiple calibrators (in a
one level nested list).

.. code-block:: python

  science_targets = ["Beta Leo", "HD 100453"]
  calibrators = [["HD100920", "HD173460"], "HD102964"]

There are two additional lists that can be specified. 
The :python:`orders` lists specifies the order of the targets after upload, where "b" stands
for before and "a" for after the science target. This results in either `SCI-CAL`, `CAL-SCI-CAL` or any combination.
The last list that can be given is the :python:`tags` list, that specifies the calibrators' tags.
The tags are 'L' for an L-band calibrator, 'N' for an N-band calibrator and "LN" for both bands.
The default is "LN" for both.
If the :python:`orders` and :python:`tags` lists are not provided by the user, they will be autofilled to have the same shape
as the :python:`calibrators` list.

.. code-block:: python

  orders = [["b", "a"], "a"]
  tags = [["L", "LN"], "N"]

These lists then need to be passes as a combined list :python:`manual_input` to the function:

.. code-block:: python

  manual_input = [sci_lst, cal_lst, tag_lst, order_lst]

With the :python:`resolutions` dictionary, one can manually set the resolution
for specific targets as keys, with the resolution as values (either *low, med or high*).

.. code-block:: python

  resolutions = {"Beta Leo": "med"}

.. warning::

   The :python:`resolution`-dictionary can and will be overwritten by any query results from
   a local catalog (see :ref:`options <p2obp.backend.options>`) if one is activated or the overwrite option
   :python:`options["resolution.overwrite"]` is set to :python:`False` (standard setting).

The operational mode (either :python:`"gr"` for GRA4MAT or
:python:`"st"` for MATISSE-standalone specifies the obs' settings).
This will either upload the obs to a the specified container (keyword
:python:`container_id` on p2)

.. code-block:: python

  ob_creation(manual_lst=manual_lst, operational_mode="both",
              resolution=resolutions, container_id=3001786,
              server="demo", password="52052")

or make them locally as (.obx)-files, if an :python:`output_dir` is specified.

.. code-block:: python

  ob_creation(manual_lst=manual_lst, operational_mode="both",
              resolution=res_dict, output_dir=output_dir)

For this example the ob will be uploaded to ESO's demo environment
(https://www.eso.org/p2demo/home) to the subfolder :python:`p2obp/` of the
run `60.A-9252(N) MATISSE`.


Night Plan based Creation
-------------------------

