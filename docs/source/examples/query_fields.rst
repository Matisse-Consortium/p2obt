============
Query Fields
============

This is a list of all the queryable fields for the different catalogs, that can be
specified by the user in the :ref:`options <p2obp.backend.options>`.

Simbad
======

.. code-block:: python

  'MAIN_ID', 'RA', 'DEC', 'RA_PREC', 'DEC_PREC',
  'COO_ERR_MAJA', 'COO_ERR_MINA', 'COO_ERR_ANGLE',
  'COO_QUAL', 'COO_WAVELENGTH', 'COO_BIBCODE',
  'MK_ds', 'MK_mss', 'MK_Spectral_type', 'MK_bibcode',
  'SP_TYPE', 'SP_TYPE_2', 'SP_QUAL', 'SP_BIBCODE',
  'Fe_H_Teff', 'Fe_H_log_g', 'Fe_H_Fe_H', 'Fe_H_flag',
  'Fe_H_CompStar', 'Fe_H_CatNo', 'Fe_H_bibcode', 'PMRA',
  'PMDEC', 'PM_ERR_MAJA', 'PM_ERR_MINA', 'PM_ERR_ANGLE',
  'PLX_VALUE', 'RV_VALUE', 'FLUX_U', 'FLUX_ERROR_U',
  'FLUX_B', 'FLUX_ERROR_B', 'FLUX_V', 'FLUX_ERROR_V',
  'FLUX_R', 'FLUX_ERROR_R', 'FLUX_I', 'FLUX_ERROR_I',
  'FLUX_J', 'FLUX_ERROR_J', 'FLUX_H', 'FLUX_ERROR_H',
  'FLUX_K', 'FLUX_ERROR_K'

GAIA
====

.. code-block:: python

  'RA_ICRS', 'e_RA_ICRS', 'DE_ICRS', 'e_DE_ICRS',
  'Source', 'Plx', 'e_Plx', 'pmRA', 'e_pmRA',
  'pmDE', 'e_pmDE', 'Dup', 'FG', 'e_FG', 'Gmag',
  'e_Gmag', 'FBP', 'e_FBP', 'BPmag', 'e_BPmag',
  'FRP', 'e_FRP', 'RPmag', 'e_RPmag', 'BP-RP',
  'RV', 'e_RV', 'Teff', 'AG', 'E_BP-RP_', 'Rad', 'Lum'

TYCHO
=====

.. code-block:: python

  'e_BTmag', 'e_VTmag', 'IDTyc2', 'RAT',
  'DET', 'pmRA', 'pmDE', 'EpRA1990',
  'EpDE1990', 'CCDM', 'BTmag', 'VTmag',
  'TDSC', 'WDS', 'PA', 'Sep', '_RA.icrs', '_DE.icrs'

NOMAD
=====

.. code-block:: python

  'NOMAD1', 'YM', 'RAJ2000', 'DEJ2000', 'r',
  'pmRA', 'e_pmRA', 'pmDE', 'e_pmDE', 'Bmag',
  'r_Bmag', 'Vmag', 'r_Vmag', 'Rmag', 'r_Rmag',
  'Jmag', 'Hmag', 'Kmag', 'R'

2MASS
=====

.. code-block:: python

  'RAJ2000', 'DEJ2000', '_2MASS', 'Jmag',
  'e_Jmag', 'Hmag', 'e_Hmag', 'Kmag', 'e_Kmag',
  'Qflg', 'Rflg', 'Bflg', 'Cflg', 'Xflg', 'Aflg'

WISE
====

.. code-block:: python

  'RAJ2000', 'DEJ2000', 'eeMaj', 'eeMin', 'Im',
  'W1mag', 'e_W1mag', 'W2mag', 'e_W2mag',
  'W3mag', 'e_W3mag', 'W4mag', 'e_W4mag',
  'Jmag', 'Hmag', 'Kmag', 'ccf', 'ex', 'var', 'd2M', '_2M'

MDFC
====

.. code-block:: python

  '_r', 'Name', 'SpType', 'RAJ2000', 'DEJ2000',
  'Dist', 'Teff-MIDI', 'Teff-GAIA', 'Comp',
  'Mean-sep', 'mag1', 'mag2', 'Diam-MIDI',
  'e_Diam-MIDI', 'Diam-Cohen', 'e_Diam-Cohen',
  'Diam-GAIA', 'LDD-meas', 'e_LDD-meas', 'UDD-meas',
  'Band-meas', 'LDD-est', 'e_LDD-est', 'UDDL-est',
  'UDDM-est', 'UDDN-est', 'Jmag', 'Hmag', 'Kmag',
  'W4mag', 'CalFlag', 'IRflag', 'nb-Lflux',
  'med-Lflux', 'disp-Lflux', 'nb-Mflux', 'med-Mflux',
  'disp-Mflux', 'nb-Nflux', 'med-Nflux', 'disp-Nflux',
  'Lcorflux30', 'Lcorflux100', 'Lcorflux130', 'Mcorflux30',
  'Mcorflux100', 'Mcorflux130', 'Ncorflux30',
  'Ncorflux100', 'Ncorflux130', 'Simbad'

