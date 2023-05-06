.. _installation:

.. role:: python(code)
   :language: python

============
Installation
============

.. sourcecode:: bash
 
  pip install git+https://github.com/MBSck/p2obp.git


Optional
============

An optional dependency is R. van Boekel's :python:`calibrator_find.pro`.
This is an IDL software used for calibrator finding, from which 
night_plans can be manually created.
These are then used to feed the :mod:`parse <p2obp.backend.parse>` of :python:`p2obp`
used within the :func:`create_obs <p2obp.automate.create_obs>`.
