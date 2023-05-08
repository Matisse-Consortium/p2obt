.. _options:

.. role:: python(code)
   :language: python

=====================
p2obp.backend.options
=====================


The global settings for :python:`p2obp` are contained in a dictionary and can be
changed by the user. Hereafter follows a list of all the availabe options 
that can be changed and their default values as seen in the script :python:`options`.

---------------
Logger Settings
---------------

The logging settings that are used for logging errors.

.. code-block:: python

   options["logging.folder"] = "logs"
   options["logging.path"] = Path(__file__).parent.parent / options["loggging.folder"]
   options["logging.level"] = logging.DEBUG
   options["logging.format"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

-----------
OB Creation
-----------

General
=======

General settings for the pipeline-function :func:`create_obs <p2obp.automate.create_obs>`.

This option sets the central wavelength used for all observation templates.

.. code-block:: python

   options["central_wl"] = 4.1

This options sets the standard resolution for all created obs.

.. code-block:: python

   options["resolution"] = "low"

With this option one can override the resolutions queried from the local catalogs
(see :ref:`Used Catalogs`), which, as a standard, would overwrite the standard resolution
or any resolution set in an input dictionary for the :func:`create_obs <p2obp.automate.create_obs>` function.

.. code-block:: python

   options["resolution.overwrite"] = False

Integration time
================

The integration times for MATISSE-standalone for the ATs.

.. code-block:: python

   options["dit.matisse.ats.low"] = 0.111
   options["dit.matisse.ats.med"] = 0.111
   options["dit.matisse.ats.high"] = 0.111

The integration times for MATISSE-standalone for the UTs.

.. code-block:: python

   options["dit.matisse.uts.low"] = 0.111
   options["dit.matisse.uts.med"] = 0.111
   options["dit.matisse.uts.high"] = 0.111

The integration times for GRA4MAT for the ATs.

.. code-block:: python

   options["dit.gra4mat.ats.low"] = 0.6
   options["dit.gra4mat.ats.med"] = 1.3
   options["dit.gra4mat.ats.high"] = 3.

The integration times for GRA4MAT for the UTs.

.. code-block:: python

   options["dit.gra4mat.uts.low"] = 0.6
   options["dit.gra4mat.uts.med"] = 0.6
   options["dit.gra4mat.uts.high"] = 0.6

-----
Query
-----

The settings used for the :func:`query <p2obp.backend.query.query>` function.

Used Catalogs
=============

.. code-block:: python

   options["catalogs"] = ["gaia", "tycho", "nomad",
                          "2mass", "wise", "mdfc",
                          "simbad", "local"]

The local catalogs/databases queried.

.. code-block:: python

   options["catalogs.local.standard"] = "Targets"
   options["catalogs.local.ciao"] = "CIAO Offaxis Targets"

Setting the following option to either :python:`ciao` or :python:`standard` will query one of
the above catalogs. If the options is set to :python:`none`, no local catalog will be queried.
But this can be easier done with the :func:`query <p2obp.backend.query.query>` function by excluding
the :python:`local` catalog.

.. code-block:: python

   options["catalogs.local.active"] = "standard"

The online catalogs queried.

.. code-block:: python

   options["catalogs.gaia.catalog"] = "I/345/gaia2"
   options["catalogs.tycho.catalog"] = "I/350/tyc2tdsc"
   options["catalogs.nomad.catalog"] = "I/297/out"
   options["catalogs.2mass.catalog"] = "II/246/out"
   options["catalogs.wise.catalog"] = "II/311/wise"
   options["catalogs.mdfc.catalog"] = "II/361/mdfc-v10"


Catalog fields
==============

Set the fields accessed in each catalog.

.. code-block:: python

   options["catalogs.gaia.fields"] = ["*"]
   options["catalogs.tycho.fields"] = ["*", "e_BTmag", "e_VTmag"]
   options["catalogs.nomad.fields"] = ["*"]
   options["catalogs.2mass.fields"] = ["*"]
   options["catalogs.wise.fields"] = ["*"]
   options["catalogs.mdfc.fields"] = ["**"]
   options["catalogs.simbad.fields"] = ["mk", "sp", "sptype", "fe_h",
                                        "pm", "plx", "rv_value",
                                        "flux(U)", "flux_error(U)",
                                        "flux(B)", "flux_error(B)",
                                        "flux(V)", "flux_error(V)",
                                        "flux(R)", "flux_error(R)",
                                        "flux(I)", "flux_error(I)",
                                        "flux(J)", "flux_error(J)",
                                        "flux(H)", "flux_error(H)",
                                        "flux(K)", "flux_error(K)"]

Catalog queries
===============

The queries that are collected from each catalog.

.. code-block:: python

   options["catalogs.gaia.query"] = ["Gmag", "pmRA", "pmDE"]
   options["catalogs.tycho.query"] = ["VTmag"]
   options["catalogs.2mass.query"] = ["Jmag", "Hmag", "Kmag"]
   options["catalogs.nomad.query"] = ["Vmag"]
   options["catalogs.wise.query"] = ["W1mag", "W3mag", "Hmag", "Kmag"]
   options["catalogs.mdfc.query"] = ["med-Lflux", "med-Nflux", "Hmag", "Kmag"]
   options["catalogs.simbad.query"] = ["RA", "DEC", "PMRA", "PMDEC",
                                       "FLUX_V", "FLUX_H", "FLUX_K"]

.. note::

   The possible fields for the catalogs are the following

   For :python:`simbad`:

   .. code-block:: python

      'MAIN_ID', 'RA', 'DEC', 'RA_PREC', 'DEC_PREC', 'COO_ERR_MAJA',
      'COO_ERR_MINA', 'COO_ERR_ANGLE', 'COO_QUAL', 'COO_WAVELENGTH', 'COO_BIBCODE',
      'MK_ds', 'MK_mss', 'MK_Spectral_type', 'MK_bibcode', 'SP_TYPE', 'SP_TYPE_2',
      'SP_QUAL', 'SP_BIBCODE', 'Fe_H_Teff', 'Fe_H_log_g', 'Fe_H_Fe_H', 'Fe_H_flag',
      'Fe_H_CompStar', 'Fe_H_CatNo', 'Fe_H_bibcode', 'PMRA', 'PMDEC', 'PM_ERR_MAJA',
      'PM_ERR_MINA', 'PM_ERR_ANGLE', 'PLX_VALUE', 'RV_VALUE', 'FLUX_U', 'FLUX_ERROR_U',
      'FLUX_B', 'FLUX_ERROR_B', 'FLUX_V', 'FLUX_ERROR_V', 'FLUX_R', 'FLUX_ERROR_R',
      'FLUX_I', 'FLUX_ERROR_I', 'FLUX_J', 'FLUX_ERROR_J', 'FLUX_H', 'FLUX_ERROR_H',
      'FLUX_K', 'FLUX_ERROR_K'
