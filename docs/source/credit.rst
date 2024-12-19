.. role:: bash(code)
   :language: bash

======
Credit
======

Many thanks to...

* J. Varga whose :bash:`MATISSE_create_OB_2` and :bash:`query_CDS` scripts have heavily inspired, and are the basis from which the :mod:`compose <p2obt.backend.compose>` and :mod:`query <p2obt.backend.query>` modules have been constructed.
* M. Pruemm whose `loadobx <https://gist.github.com/Codo3/66432a2c2ebbcd76c9e254a705a79577>`_ script partially contributed to the :mod:`upload <p2obt.backend.upload>` and :mod:`compose <p2obt.backend.compose>` modules.
* T. Bierwirth for the `p2api <https://www.eso.org/sci/observing/phase2/p2intro/Phase2API/api--python-programming-tutorial.html>`_ that provides the api-backend for the :mod:`upload <p2obt.backend.upload>` module.
* R. van Boekel for his :bash:`calibrator_find.pro` software (not included in :bash:`p2obt`, optional), that is used for the night plans, which can be parsed with the :mod:`parse <p2obt.backend.parse>` module.
