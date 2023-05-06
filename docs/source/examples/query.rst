.. role:: python(code)
   :language: python

=====
Query
=====

This script is meant to give an example on how to use the
the `query`-function of p2obp to get information on a target.

Simple query
==============

Queries the target 'HD 142666', and by default the following
catalogs: 'simbad', 'nomad', 'mdfc', 'gaia', 'tycho', '2mass' and 'wise'.
The catalogs can be either set manually with the 'catalogs' keyword
or specific ones excluded with the 'exclude_catalogs' (both take
a list as input). Further can the 'match_radius' be determined (in arcsec).

.. code-block:: python

  target = query("HD 142666")
  print("Query with standard settings:")

Speficying accessed fields
==========================

The accessed fields can be modified with the options dictionary (this
also applies for the 'catalog' and the 'fields').

.. code-block:: python

  options["catalogs.tycho.catalog"] = "..."
  options["catalogs.tycho.query"] = ["...", "..."]
  options["catalogs.tycho.fields"] = ["**"]

For more information see :ref:`options <p2obp.backend.options>`

Query with excluded catalogs
==========================

Catalogs can also be excluded via (this can results in errors if all or
too many are excluded)

.. code-block:: python

  target = query("HD 142666", exclude_catalogs=["tycho"])

Querying local catalog
==========================

There are also two local catalogs present. The active one is by default
the 'standard'-local catalog as there might be a target overlap for different
purposes

.. code-block:: python

  target = query("M8E-IR")

Querying different local catalog
==========================

The local catalog for the CIAO Offaxis observations can be activated
with the options

.. code-block:: python

  options["catalogs.local.active"] = "ciao"

.. note::
   
  The local catalogs' options are either :python:`"ciao"` or :python:`"standard`
  (For more information see :ref:`options <p2obp.backend.options>`)


.. code-block:: python

  target = query("YLW 16A")
