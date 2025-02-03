.. p2obt documentation master file, created by
   sphinx-quickstart on Fri May  5 13:26:53 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========================================
P2OBT: Automated Observation Preparation
========================================

The Phase 2 OB tools (p2obt) have been made to streamline/automate
the process of MATISSE observation preparation on p2.

It queries databases, creates either obs as dictionaries or (.obx)-files and can then
upload those directly (with or without local creation) to ESO's P2 environment.

For more information on the specific capabilities of this software see :ref:`Features <features>`.

.. note::

   The `p2obt` software makes (among others) three main functions directly available to the user:

   * The :func:`query <p2obt.backend.query.query>` function, that gives the user direct information on the target.
   * The :func:`create_ob <p2obt.automate.create_ob>` function, which makes singular ob-creation and upload possible.
   * The :func:`create_obs <p2obt.automate.create_obs>` function, which has the capability of fully automated night/observation plan
     parsing and from this ob creation and upload. Alternatively, it also provides the same
     automated (local (.obx)) creation and upload for manual input.


   .. code-block:: bash
     :caption: Quick Installation

     pip install git+https://github.com/Matisse-Consortium/p2obt.git

   For more information see :ref:`Getting Started <getting_started>`

.. toctree::
   :hidden:
   :maxdepth: 2

   getting_started
   features
   api
   Changelog <https://github.com/MBSck/p2obt/releases>
   credit

* :ref:`genindex`
* :ref:`modindex`
