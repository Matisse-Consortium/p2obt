===========
OB Creation
===========

------------------
Single OB Creation
------------------

Local Creation
--------------

Upload
------


--------------------
OB creation pipeline
--------------------

This is meant to give an example on how to use the
fully automated pipeline of p2obp for ob-creation
:func:`create_obs <p2obp.automate.create_obs>`.

Manual Creation
---------------

The science targets will be assigned to the calibrators
and one science target can have multiple calibrators (in a
nested list).

.. code-block:: python

  sci_lst = ["Beta Leo", "HD 100453"]
  cal_lst = [["HD100920", "HD173460"], "HD102964"]

These lists specify the order. SCI-CAL, CAL-SCI-CAL
or any combination as well as the calirators' tags. 'L', 'N'
or 'LN'. By default they will be filled with 'a' (for after)
and 'LN' and can be left empty.

.. code-block:: python

  order_lst = [["b", "a"], "a"]
  tag_lst = [["L", "LN"], "N"]

To pass manual input to the program, make a list of lists.

.. code-block:: python

  manual_lst = [sci_lst, cal_lst, tag_lst, order_lst]

With the resolution_dict, one can manually set the resolution
for specific targets as keys, with the resolution as values.

.. code-block:: python

  res_dict = {"Beta Leo": "med"}

The resolution for all other targets will be 'low', but can be
set via the options (see :ref:`options` for a more comprehensive listing).

.. code-block:: python

  options["resolution"] = "low"

The operational mode (either 'gr' for 'GRA4MAT' or 'st' for
'MATISSE'-standalone specifies the obs' settings).
This will either upload the obs to a the specified container (keyword
'container_id' on p2) or make them locally, if an 'output_dir' is
specified.

.. code-block:: python

  ob_creation(manual_lst=manual_lst, operational_mode="both",
              resolution=res_dict, output_dir=output_dir)


Night Plan based Creation
-------------------------

