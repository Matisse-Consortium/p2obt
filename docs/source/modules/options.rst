.. _options:

.. role:: python(code)
   :language: python

=====================
p2obt.backend.options
=====================

The global settings for :python:`p2obt` are contained in a dictionary and can be
changed by the user. Hereafter follows a list of all the availabe options 
that can be changed and their default values as seen in the script :python:`options`.

---------------
Logger Settings
---------------

The logging settings that are used for logging errors.

.. code-block:: python

   OPTIONS.log.path = Path(__file__).parent.parent / "logs"
   OPTIONS.log.level = logging.DEBUG
   OPTIONS.log.format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

-----------
OB Creation
-----------

General settings for the pipeline-function :func:`create_obs <p2obt.automate.create_obs>`.

Resolution
==========

This options sets the standard resolution for all created obs.

.. code-block:: python

   OPTIONS.resolution.active = "low"

With this option one can override the resolutions queried from the local catalogs
(see :ref:`Used Catalogs`), which, as a standard, would overwrite the standard resolution
or any resolution set in an input dictionary for the :func:`create_obs <p2obt.automate.create_obs>` function.

.. code-block:: python

   OPTIONS.resolution.overwrite = False

Photometry
==========

The default photometry settings for MATISSE-standalone

.. code-block:: python

   OPTIONS.photometry.matisse.ats = True
   OPTIONS.photometry.matisse.uts = True

The photometry settings for GRA4MAT

.. code-block:: python

   OPTIONS.photometry.gra4mat.ats = True
   OPTIONS.photometry.gra4mat.uts = False

Integration time
================

The default integration times for MATISSE-standalone for the ATs.

.. code-block:: python

   OPTIONS.dit.matisse.ats.low = 0.111
   OPTIONS.dit.matisse.ats.med = 0.111
   OPTIONS.dit.matisse.ats.high = 0.111

The default integration times for MATISSE-standalone for the UTs.

.. code-block:: python

   OPTIONS.dit.matisse.uts.low = 0.111
   OPTIONS.dit.matisse.uts.med = 0.111
   OPTIONS.dit.matisse.uts.high = 0.111

The default integration times for GRA4MAT for the ATs.

.. code-block:: python

   OPTIONS.dit.gra4mat.ats.low = 0.6
   OPTIONS.dit.gra4mat.ats.med = 1.3
   OPTIONS.dit.gra4mat.ats.high = 3.

The default integration times for GRA4MAT for the UTs.

.. code-block:: python

   OPTIONS.dit.gra4mat.uts.low = 0.6
   OPTIONS.dit.gra4mat.uts.med = 0.6
   OPTIONS.dit.gra4mat.uts.high = 0.6

Central wavelength
==================

The default central wavelengths for MATISSE-standalone for the ATs.

.. code-block:: python

   OPTIONS.wl0.matisse.ats.low = 4.1
   OPTIONS.wl0.matisse.ats.med = 4.1
   OPTIONS.wl0.matisse.ats.high = 4.1

The default central wavelengths for MATISSE-standalone for the UTs.

.. code-block:: python

   OPTIONS.wl0.matisse.uts.low = 4.1
   OPTIONS.wl0.matisse.uts.med = 4.1
   OPTIONS.wl0.matisse.uts.high = 4.1


The default central wavelengths for GRA4MAT for the ATs.

.. code-block:: python

   OPTIONS.wl0.gra4mat.ats.low = 4.1
   OPTIONS.wl0.gra4mat.ats.med = 4.1
   OPTIONS.wl0.gra4mat.ats.high = 4.1


The default central wavelengths for GRA4MAT for the UTs.

.. code-block:: python

   OPTIONS.wl0.gra4mat.uts.low = 4.1
   OPTIONS.wl0.gra4mat.uts.med = 3.52
   OPTIONS.wl0.gra4mat.uts.high = 3.52

-----
Query
-----

The settings used for the :func:`query <p2obt.backend.query.query>` function.

Used Catalogs
=============

.. code-block:: python

   OPTIONS.catalogs = ["gaia", "tycho", "nomad",
                       "two_mass", "wise", "mdfc",
                       "simbad", "local"]

The local catalogs/databases queried.

.. code-block:: python

   OPTIONS.catalogs.local.standard = "Targets"
   OPTIONS.catalogs.local.ciao = "CIAO Offaxis Targets"

Setting the following option to either :python:`ciao` or :python:`standard` will query one of
the above catalogs. If the option is set to :python:`none`, no local catalog will be queried.
But this can be easier done with the :func:`query <p2obt.backend.query.query>` function by excluding
the :python:`local` catalog.

.. code-block:: python

   OPTIONS.catalogs.local.active = "standard"

The online catalogs queried.

.. code-block:: python

   OPTIONS.catalogs.gaia.catalog = "I/345/gaia2"
   OPTIONS.catalogs.tycho.catalog = "I/350/tyc2tdsc"
   OPTIONS.catalogs.nomad.catalog = "I/297/out"
   OPTIONS.catalogs.two_mass.catalog = "II/246/out"
   OPTIONS.catalogs.wise.catalog = "II/311/wise"
   OPTIONS.catalogs.mdfc.catalog = "II/361/mdfc-v10"


Catalog fields
==============

Set the fields accessed in each catalog.

.. code-block:: python

   OPTIONS.catalogs.gaia.fields = ["*"]
   OPTIONS.catalogs.tycho.fields = ["*", "e_BTmag", "e_VTmag"]
   OPTIONS.catalogs.nomad.fields = ["*"]
   OPTIONS.catalogs.two_mass.fields = ["*"]
   OPTIONS.catalogs.wise.fields = ["*"]
   OPTIONS.catalogs.mdfc.fields = ["**"]
   OPTIONS.catalogs.simbad.fields = ["mk", "sp", "sptype", "fe_h",
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

   OPTIONS.catalogs.gaia.query = ["Gmag", "pmRA", "pmDE"]
   OPTIONS.catalogs.tycho.query = ["VTmag"]
   OPTIONS.catalogs.two_mass.query = ["Jmag", "Hmag", "Kmag"]
   OPTIONS.catalogs.nomad.query = ["Vmag"]
   OPTIONS.catalogs.wise.query = ["W1mag", "W3mag", "Hmag", "Kmag"]
   OPTIONS.catalogs.mdfc.query = ["med-Lflux", "med-Nflux", "Hmag", "Kmag"]
   OPTIONS.catalogs.simbad.query = ["RA", "DEC", "PMRA", "PMDEC",
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
