# P2obp
<!-- Project Shields -->
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
![Lifecycle: production](https://img.shields.io/badge/lifecycle-production-orange.svg)

The Phase 2 OB Pipeline (p2obp) has been made to streamline/automate
the process of MATISSE observation preparation on p2.

* **Documentation**: _Soon to come!_ (Right now see [Features](#features))
* **Installation**: [Installation](#installation)
* **Usage**: [Usage](#usage) and the scripts in the `example/` directory.
* **Bug Reports**: [https://github.com/MBSck/p2obp/issues](https://github.com/MBSck/p2obp/issues)
* **Contact**: [Contributors](#contributors)

<!-- USAGE EXAMPLES -->
## Usage
The `p2obp` software makes three functions directly available to the user:
* The `query` script, that gives the user direct information on the target.
* The `create_ob` script, which makes singular ob-creation and upload possible.
* The `create_obs` script, which has the capability of fully automated
night/observation plan parsing and from this ob creation and upload. Alternatively, it
also provides the same automated (local (.obx)) creation and upload for manual input.<br><br>
For examples of the above scripts' usage, see the `examples/`-directory.<br>

## Resources
* [Phase 2 API](https://www.eso.org/sci/observing/phase2/p2intro/Phase2API.html)
* [User-contributed software ESO](https://www.eso.org/sci/observing/phase2/p2intro/Phase2API/ApiContributedSoftware.html)

<!-- Credit -->
## Credit
### Used Code by
* T. Bierwirth `p2api`
* R. van Boekel `calibrator_find.pro`, not included in this repo and optional

### Inspiration
Thanks to...
* M. Pruemm whose `loadobxy` script inspired the
`p2obp.backend.upload` and `p2obp.backend.compose` scripts.
* J. Varga whose `MATISSE_create_OB_2.py` and `query_CDS.py` scripts inspired
the `p2obp.backend.query` and `p2obp.backend.compose` scripts.

### Contributors
* [M. B. Scheuck](https://www.github.com/MBSck/)
