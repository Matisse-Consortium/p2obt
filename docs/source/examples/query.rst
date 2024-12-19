.. role:: python(code)
   :language: python

=====
Query
=====

.. toctree::
   :hidden:

   query_fields

This script is meant to give an example on how to use the
the `query`-function of p2obt to get information on a target.

.. note::

   The :func:`query <p2obt.backend.query.query>` function is based on a local
   catalog query (see `Querying Local Catalogs`) as well as a query of :python:`Vizier`
   based catalogs (see `Simple Query` and `Vizier Queries <https://astroquery.readthedocs.io/en/latest/vizier/vizier.html>`_).

------------
Simple Query
------------

Queries the target 'HD 142666', and by default the following
catalogs: 'simbad', 'nomad', 'mdfc', 'gaia', 'tycho', '2mass' and 'wise'.
The catalogs can be either set manually with the 'catalogs' keyword
or specific ones excluded with the 'exclude_catalogs' (both take
a list as input). Further can the 'match_radius' be determined (in arcsec).

.. code-block:: python

  target = query("HD 142666")
  print("Query with standard settings:")

.. note::

   Some astronomical objects can have their object type as a prefix.
   :python:`p2obt` takes care of that by automatically adding this prefix if the
   target can not be found in, for instance, :python:`simbad`.
   For a comprehensive list see `simbad object types <https://simbad.cds.unistra.fr/guide/otypes.htx>`_.

---------------------
Customization Options
---------------------

There are various settings that enable a more user-tailored query.
In the following, some examples of these are presented.

.. note::

  For more information on the all the available settings see :ref:`options <p2obt.backend.options>`.

Specifying accessed fields
==========================

The accessed fields can be modified with the :python:`OPTIONS` :python:`SimpleNamespace` (this
also applies for the :python:`"catalog"` and the :python:`"queries"`).

.. code-block:: python

  OPTIONS.catalogs.tycho.catalog = "..."
  OPTIONS.catalogs.tycho.query = ["...", "..."]
  OPTIONS.catalogs.tycho.fields = ["**"]

Query with excluded catalogs
==========================

Catalogs can also be excluded via the :python:`exclude_catalogs` keyword.

.. code-block:: python

  target = query("HD 142666", exclude_catalogs=["tycho"])

.. warning::

  This can result in errors if too many or all catalogs are excluded.

Querying Local Catalogs
=======================

There are also two local catalogs present in :python:`p2obt`, which exists in order
to provide either better/more accurate data on a target, or any data at all if the target
is not listed in the online catalogs, or listed under another name.

.. note::

   These are the catalogs :python:`"standard"` and :python:`"ciao"`, which are
   separated, as there exists target overlaps with different values.
   (For more information on the local and all catalogs see :ref:`options <p2obt.backend.options>`)

   .. warning::

     Be aware that not all targets of one catalog exist in the other. This can
     result in query errors, if the target is also not found in an online catalog.
   
The one queried by default is the :python:`"standard"` catalog.

.. code-block:: python

  target = query("M8E-IR")

Changing the local catalog
--------------------------

In order to change the active local catalog, to, in this case, the one used for the CIAO Offaxis observations
:python:`"ciao"` one needs to change the following setting:

.. code-block:: python

  OPTIONS.catalogs.local.active = "ciao"


And now the target :python:`"YLW 16A`, which is not present in the :python:`"standard"` catalog
can be queried.

.. code-block:: python

  target = query("YLW 16A")
