.. _installation:

.. role:: bash(code)
   :language: bash

============
Installation
============

.. sourcecode:: bash

   pip install git+https://github.com/Matisse-Consortium/p2obt.git

or clone from source and install locally (with or without dev-dependencies):

.. sourcecode:: bash
  
  git clone git@github.com:MBSck/p2obt.git
  cd p2obt && pip install -e .[dev]

Optional
========

An optional dependency is R. van Boekel's :bash:`calibrator_find.pro`.
This is an IDL software used for calibrator finding, from which 
night_plans can be manually created. This might be converted into a dedicated
python software in the future.

These are then used to feed the :mod:`parse <p2obt.backend.parse>` module of :bash:`p2obt`
used within the :func:`create_obs <p2obt.automate.create_obs>` (see :ref:`features`).
